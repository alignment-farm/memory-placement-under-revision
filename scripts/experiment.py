"""Causal online EARM plus equal-evidence controls, with acquired-score replay logs."""
import argparse
import copy
import dataclasses
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path
import numpy as np
from rank_bm25 import BM25Okapi
from workload import documents, stream, dump_json
from runtime import Runtime, SCORE_PREFIX, ANSWER_PREFIX, document_text, parse_answer
from retrieval import Index

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'downloads/earm/src'))
from earm.online import EARMState,EARMConfig,OnlineCandidate

def tokens(text):return re.findall(r'[a-z]+|\d+',text.lower())
def correct(answer,gold):
    if not isinstance(answer,list) or len(answer)!=len(gold):return False
    return all((type(a) is bool and a==g) if type(g) is bool else
               (type(a) in (int,float) and abs(a-g)<1e-6) for a,g in zip(answer,gold))

def run(args):
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic()
    cfg=EARMConfig(block_size=4,budgets=(12,6,4,3),rank=args.rank,l2=.1,max_iterations=500,tolerance=1e-6,seed=args.seed)
    manifest=dict(args=vars(args),earm=dataclasses.asdict(cfg),git_revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  source_dirty=subprocess.check_output(['git','status','--porcelain'],text=True),
                  model_revision='cdbee75f17c01a7cc42f958dc650907174af0554',started=time.time())
    dump_json(out/'manifest.json',manifest)
    base=documents()
    for v in ('v0','narrow','broad'):dump_json(out/f'documents-{v}.json',documents(v))
    seen=set()
    for path in args.exclude:
        seen.update(c['question'] for c in json.loads(Path(path).read_text()))
    initial=stream(args.seed,args.initial,prefix='acquire',seen=seen)
    branches={name:stream(args.seed+100+i,args.after,version=v,shifted=s,prefix=name,seen=seen)
              for i,(name,v,s) in enumerate([('stable','v0',False),('content_narrow','narrow',False),
                                            ('content_broad','broad',False),('evidence','v0',True),('combined','broad',True)])}
    cases=initial+sum(branches.values(),[])
    assert len({c['question'] for c in cases})==len(cases),'Duplicate requests'
    dump_json(out/'evaluation-only.json',cases)
    rt=Runtime(out)
    allrows=[]
    states={'retain':EARMState(cfg),'invalidate':EARMState(cfg)}

    def process(cases,states):
        version=cases[0]['version'];tick=time.monotonic()
        docs=documents(version);by_id={d['id']:d for d in docs}
        changed={d['id'] for d,b in zip(docs,base) if d['sha256']!=b['sha256']}
        index=Index(docs)
        revision_seconds=time.monotonic()-tick
        for qi,case in enumerate(cases):
            q=case['question'];tick=time.monotonic()
            semantic=index.scores(q,args.entity)
            lexical=sorted(by_id,key=lambda x:(-semantic[x],x))
            lexical_seconds=time.monotonic()-tick
            scores={};scorecalls={};ranks={};costs={};diag={}
            def acquire(ids):
                for mid in ids:
                    if mid not in scores:
                        call=rt.call('score',SCORE_PREFIX+document_text(by_id[mid]),q,12)
                        raw=call['raw'].strip()
                        try:score=float(raw)
                        except ValueError:raise ValueError(f'Invalid score {raw!r}: {case["id"]} {mid}')
                        assert 0<=score<=1
                        scores[mid]=score;scorecalls[mid]=call
                return {mid:scores[mid] for mid in ids}
            for arm,state in states.items():
                def identity(mid):return mid+'@'+version if arm=='invalidate' and mid in changed else mid
                reverse={identity(mid):mid for mid in by_id}
                candidates=[OnlineCandidate(identity(mid),semantic[mid]) for mid in by_id]
                acquired=[];callback_seconds=[0.]
                def scorer(query,requested):
                    callback_start=time.monotonic()
                    mids=[reverse[x.memory_id] for x in requested]
                    acquired.extend(mids)
                    observed=acquire(mids)
                    callback_seconds[0]+=time.monotonic()-callback_start
                    return {identity(mid):val for mid,val in observed.items()}
                tick=time.monotonic();ranking=state.process_query(case['id'],q,candidates,scorer)
                elapsed=time.monotonic()-tick
                scored_seconds=sum(scorecalls[mid]['seconds'] for mid in acquired)
                # Callback may reuse paid observations between arms. Measure ALS separately below.
                order=[reverse[x.memory_id] for x in ranking.memories]
                ranks['earm_'+arm]=order[:args.top_k]
                costs['earm_'+arm]=dict(acquired=acquired,score_calls=len(acquired),cold_extra=ranking.cold_start_extra_calls,
                    fit_iterations=ranking.fit_iterations,fit_converged=ranking.fit_converged,
                    process_seconds=elapsed,learning_seconds=elapsed-callback_seconds[0],score_seconds=scored_seconds,
                    model_bytes=sum(getattr(state.model,k).nbytes for k in ('values','structural_mask','row_bias','column_bias','row_factors','column_factors')))
                diag[arm]=dict(predicted={reverse[x.memory_id]:x.final_score for x in ranking.memories},observed=acquired)
                if arm=='retain':
                    ranks['observed']=sorted(acquired,key=lambda x:(-scores[x],-semantic[x],x))[:args.top_k]
                    costs['observed']=dict(acquired=list(acquired),score_calls=len(acquired),score_seconds=scored_seconds)
            # Full scores are acquired only after both causal learners finish this request.
            acquire(list(by_id))
            ranks['bm25']=lexical[:args.top_k]
            ranks['full_rerank']=sorted(by_id,key=lambda x:(-scores[x],-semantic[x],x))[:args.top_k]
            ranks['full_context']=list(by_id)
            costs['bm25']=dict(score_calls=0,score_seconds=0)
            costs['full_context']=dict(score_calls=0,score_seconds=0)
            costs['full_rerank']=dict(score_calls=len(docs),score_seconds=sum(c['seconds'] for c in scorecalls.values()))
            for arm,d in diag.items():
                unseen=set(by_id)-set(d['observed'])
                anchor_mean=np.mean([scores[m] for m in d['observed']])
                d['unobserved_mse']=float(np.mean([(d['predicted'][m]-scores[m])**2 for m in unseen])) if unseen else None
                d['anchor_mean_mse']=float(np.mean([(anchor_mean-scores[m])**2 for m in unseen])) if unseen else None
            answers={}
            for arm,selected in ranks.items():
                # Canonical context order isolates selection from document-order effects.
                selected=sorted(selected)
                answer_query=q+('\nShow the applicable numeric rule and all three calculations before your final JSON; do not skip them.' if args.explain else '')
                call=rt.call('answer',ANSWER_PREFIX+'\n\n'.join(document_text(by_id[mid]) for mid in selected),answer_query,args.answer_limit)
                parsed=parse_answer(call['raw'])
                answers[arm]=dict(selected=selected,answer=parsed,correct=correct(parsed,case['gold']),
                                  stale=case['affected'] and correct(parsed,case['old_gold']),
                                  support_hit=bool(set(selected)&set(case['supports'])),
                                  imputed_selected=[m for m in selected if arm.startswith('earm_') and m not in costs[arm]['acquired']],
                                  answer_call=call['call_id'],answer_seconds=call['seconds'],prompt_tokens=call['prompt_tokens'],
                                  cached_tokens=call['cached_tokens'],completion_tokens=call['completion_tokens'],
                                  experimental_reuse=call['experimental_reuse'],cost=costs[arm])
            row=dict(case=case,answers=answers,scores=scores,score_call_ids={m:c['call_id'] for m,c in scorecalls.items()},
                     diagnostic=diag,lexical_seconds=lexical_seconds,revision_seconds=revision_seconds if qi==0 else 0)
            allrows.append(row)
            with (out/'results.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
            print(json.dumps(dict(case=case['id'],correct={a:r['correct'] for a,r in answers.items()},calls=rt.counter,seconds=round(time.monotonic()-start,1))),flush=True)
        for arm,state in states.items():state.save(out/f'{cases[0]["id"].rsplit("-",1)[0]}-{arm}.npz')

    try:
        process(initial,states)
        learned=copy.deepcopy(states)
        for name,cases in branches.items():process(cases,copy.deepcopy(learned))
        summary=dict(status='complete',seconds=time.monotonic()-start,load_seconds=rt.load_seconds,
                     wait_seconds=rt.wait_seconds,physical_model_calls=rt.counter,peak_bytes=__import__('mlx.core',fromlist=['']).get_peak_memory(),
                     cases=len(allrows),accuracy={arm:sum(r['answers'][arm]['correct'] for r in allrows)/len(allrows) for arm in allrows[0]['answers']})
        dump_json(out/'summary.json',summary);print(json.dumps(summary),flush=True)
    except BaseException as e:
        dump_json(out/'failure.json',dict(error=repr(e),seconds=time.monotonic()-start,cases_completed=len(allrows),physical_model_calls=rt.counter))
        raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--seed',type=int,default=101)
    p.add_argument('--initial',type=int,default=16);p.add_argument('--after',type=int,default=8)
    p.add_argument('--rank',type=int,default=2);p.add_argument('--top-k',type=int,default=2)
    p.add_argument('--exclude',nargs='*',default=[])
    p.add_argument('--entity',action='store_true');p.add_argument('--explain',action='store_true')
    p.add_argument('--answer-limit',type=int,default=512)
    run(p.parse_args())
