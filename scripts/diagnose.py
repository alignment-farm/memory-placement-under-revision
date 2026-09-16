"""Bounded development-only retrieval and answerer diagnosis."""
import argparse
import copy
import dataclasses
import json
import re
import sys
import time
from pathlib import Path
import numpy as np
from rank_bm25 import BM25Okapi
from workload import documents, dump_json
from runtime import Runtime,ANSWER_PREFIX,document_text,parse_answer
from experiment import correct,tokens
from earm.online import EARMState,EARMConfig,OnlineCandidate
from retrieval import Index

def priorities(docs,question,entity=False):
    return Index(docs).scores(question,entity)

def replay(rows,rank,entity):
    cfg=EARMConfig(block_size=4,budgets=(12,6,4,3),rank=rank,l2=.1,max_iterations=500,tolerance=1e-6,seed=101)
    state=EARMState(cfg);acquired=None;phase='acquire';records=[]
    for row in rows:
        case=row['case'];now=case['id'].rsplit('-',1)[0]
        if now!=phase:
            if phase=='acquire':acquired=copy.deepcopy(state)
            state=copy.deepcopy(acquired);phase=now
        docs=documents(case['version']);scores=priorities(docs,case['question'],entity)
        observations=[]
        def callback(q,cs):
            observations.extend(c.memory_id for c in cs)
            return {c.memory_id:row['scores'][c.memory_id] for c in cs}
        t=time.monotonic()
        ranking=state.process_query(case['id'],case['question'],[OnlineCandidate(m,s) for m,s in scores.items()],callback)
        mixed=[r.memory_id for r in ranking.memories[:2]]
        obs=sorted(observations,key=lambda m:(-row['scores'][m],-scores[m],m))[:2]
        lex=sorted(scores,key=lambda m:(-scores[m],m))[:2]
        predicted={r.memory_id:r.final_score for r in ranking.memories}
        unseen=set(scores)-set(observations)
        records.append(dict(id=case['id'],mixed=mixed,observed=obs,lexical=lex,
                            hits={k:bool(set(v)&set(case['supports'])) for k,v in [('mixed',mixed),('observed',obs),('lexical',lex)]},
                            imputed=sum(m not in observations for m in mixed),
                            mse=float(np.mean([(predicted[m]-row['scores'][m])**2 for m in unseen])) if unseen else None,
                            calls=len(observations),seconds=time.monotonic()-t,converged=ranking.fit_converged))
    return dict(rank=rank,entity=entity,records=records,summary=dict(hits={a:sum(r['hits'][a] for r in records) for a in ('mixed','observed','lexical')},
                n=len(records),imputed=sum(r['imputed'] for r in records),mse=float(np.mean([r['mse'] for r in records if r['mse'] is not None])),seconds=sum(r['seconds'] for r in records)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',default='evidence/development-v3');p.add_argument('--output',default='evidence/diagnosis-v1');p.add_argument('--answers',action='store_true');args=p.parse_args()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    rows=[json.loads(s) for s in (Path(args.source)/'results.jsonl').read_text().splitlines()]
    if not args.answers:
        results=[replay(rows,rank,entity) for rank,entity in [(2,False),(8,False),(2,True),(8,True)]]
        dump_json(out/'replay.json',results)
        print(json.dumps([{k:v for k,v in r.items() if k!='records'} for r in results],indent=2))
    else:
        # Fix a mix of errors and successes; no fresh material is involved.
        ids=['acquire-000','acquire-002','acquire-004','acquire-006','acquire-010','stable-000','evidence-000','evidence-001']
        selected=[r for r in rows if r['case']['id'] in ids]
        rt=Runtime(out);results=[]
        for row in selected:
            c=row['case'];docs=documents(c['version']);scores=priorities(docs,c['question'],True)
            mids=sorted(scores,key=lambda m:(-scores[m],m))[:2]
            context='\n\n'.join(document_text(d) for d in docs if d['id'] in mids)
            call=rt.call('answer',ANSWER_PREFIX+context,c['question']+'\nShow the applicable numeric rule and all three calculations before your final JSON; do not skip them.',320)
            results.append(dict(id=c['id'],gold=c['gold'],raw=call['raw'],selected=mids,correct=correct(parse_answer(call['raw']),c['gold'])))
        dump_json(out/'answer-repair.json',results);print(json.dumps(results,indent=2))
