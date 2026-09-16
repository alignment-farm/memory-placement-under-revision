"""Read-only scientific integrity audit of completed fresh runs."""
import argparse
import copy
import dataclasses
import hashlib
import json
import re
import sys
from pathlib import Path
import numpy as np
from workload import dump_json
from runtime import SCORE_PREFIX,ANSWER_PREFIX,document_text,parse_answer
from experiment import correct
from retrieval import Index
from earm.online import EARMState,EARMConfig,OnlineCandidate

def independent_gold(case,docs):
    nums=json.loads(re.search(r'\[[^\]]+\]',case['question']).group())
    by={d['id'].removeprefix('doc_checking_accounts_'):d['content'] for d in docs}
    f=case['family']
    if not case['shifted']:
        if f==0:
            threshold=int(re.search(r'minimum daily balance of \$(\d+)',by['blue_account_002']).group(1))
            return [x>=threshold for x in nums]
        if f==1:
            lo,hi=map(int,re.search(r'between (\d+) and (\d+) years',by['light_green_account_002']).groups())
        elif f==2:
            lo=int(re.search(r'at least (\d+)',by['dark_green_account_002']).group(1))
            hi=int(re.search(r'through (\d+)',by['dark_green_account_002']).group(1))
        else:
            lo=int(re.search(r'at least (\d+)',by['gold_years_account_002']).group(1));hi=200
        return [lo<=x<=hi for x in nums]
    if f==0:
        rate,minimum=re.search(r'charged (\d+)%.*minimum fee of \$([\d.]+)',by['blue_account_012']).groups()
        return [round(max(float(rate)*x/100,float(minimum)),2) for x in nums]
    if f==1:
        threshold,fee=re.search(r'Up to and including \$(\d+) \| \$([\d.]+)',by['light_green_account_013']).groups()
        nextfee=float(re.search(r'More than \$100 and up to and including \$300 \| \$([\d.]+)',by['light_green_account_013']).group(1))
        return [float(fee) if x<=int(threshold) else nextfee for x in nums]
    if f==2:
        rate,cap=map(float,re.search(r'Foreign ATM withdrawal \| ([\d.]+)% of amount \(max \$([\d.]+)\)',by['dark_green_account_002']).groups())
        assert all(x%2==0 for x in nums)
        return [round(min(rate*x/100,cap),2) for x in nums]
    balances=json.loads(re.findall(r'\[[^\]]+\]',case['question'])[1])
    fee=float(re.search(r'standard fee.*\$([\d.]+) per transaction',by['gold_years_account_002']).group(1))
    threshold=int(re.search(r'balance is \$([\d,]+) or more',by['gold_years_account_002']).group(1).replace(',',''))
    return [0. if b>=threshold else fee for b in balances]

def audit(path,previous):
    path=Path(path);manifest=json.loads((path/'manifest.json').read_text())
    summary=json.loads((path/'summary.json').read_text());assert summary['status']=='complete'
    rows=list(map(json.loads,(path/'results.jsonl').read_text().splitlines()))
    calls={c['call_id']:c for c in map(json.loads,(path/'calls.jsonl').read_text().splitlines())}
    docs={v:json.loads((path/f'documents-{v}.json').read_text()) for v in ('v0','narrow','broad')}
    assert len(calls)==summary['physical_model_calls'] and len(rows)==summary['cases']
    assert len({r['case']['question'] for r in rows})==len(rows)
    prior=set()
    for p in previous:prior.update(c['question'] for c in json.loads(Path(p).read_text()))
    assert not prior & {r['case']['question'] for r in rows}
    cfg=dict(manifest['earm']);cfg['budgets']=tuple(cfg['budgets']);cfg=EARMConfig(**cfg)
    states={a:EARMState(cfg) for a in ('retain','invalidate')};initial=None;phase='acquire';saved=0
    failures=[];truncations=[]
    def check_saved(name):
        nonlocal saved
        for arm,state in states.items():
            disk=EARMState.load(path/f'{name}-{arm}.npz')
            assert disk.model.memory_ids==state.model.memory_ids
            assert disk.model.query_ids==state.model.query_ids
            assert abs(disk.model.global_bias-state.model.global_bias)<1e-12
            for attr in ('values','structural_mask','row_bias','column_bias','row_factors','column_factors'):
                assert np.allclose(getattr(disk.model,attr),getattr(state.model,attr),atol=1e-12,rtol=1e-12,equal_nan=True), (name,arm,attr)
            saved+=1
    for row in rows:
        case=row['case'];now=case['id'].rsplit('-',1)[0]
        if now!=phase:
            check_saved(phase)
            if phase=='acquire':initial=copy.deepcopy(states)
            states=copy.deepcopy(initial);phase=now
        ds=docs[case['version']];by={d['id']:d for d in ds}
        assert independent_gold(case,ds)==case['gold']
        assert independent_gold(case,docs['v0'])==case['old_gold']
        assert case['affected']==(case['gold']!=case['old_gold'])
        for mid,cid in row['score_call_ids'].items():
            call=calls[cid]
            assert call['prompt']==SCORE_PREFIX+document_text(by[mid])+'\n\nREQUEST:\n'+case['question']
            assert float(call['raw'].strip())==row['scores'][mid]
        semantic=Index(ds).scores(case['question'],manifest['args']['entity'])
        changed={d['id'] for d,b in zip(ds,docs['v0']) if d['sha256']!=b['sha256']}
        for arm,state in states.items():
            def identity(m):return m+'@'+case['version'] if arm=='invalidate' and m in changed else m
            reverse={identity(m):m for m in by};observed=[]
            def score(q,candidates):
                observed.extend(reverse[c.memory_id] for c in candidates)
                return {c.memory_id:row['scores'][reverse[c.memory_id]] for c in candidates}
            ranking=state.process_query(case['id'],case['question'],[OnlineCandidate(identity(m),s) for m,s in semantic.items()],score)
            result=row['answers']['earm_'+arm]
            assert observed==result['cost']['acquired']
            assert ranking.actual_llm_calls==result['cost']['score_calls']
            assert ranking.cold_start_extra_calls==result['cost']['cold_extra']
            assert sorted(reverse[m.memory_id] for m in ranking.memories[:manifest['args']['top_k']])==result['selected']
        for arm,r in row['answers'].items():
            call=calls[r['answer_call']]
            q=case['question']+'\nShow the applicable numeric rule and all three calculations before your final JSON; do not skip them.'
            assert call['prompt']==ANSWER_PREFIX+'\n\n'.join(document_text(by[m]) for m in r['selected'])+'\n\nREQUEST:\n'+q
            assert parse_answer(call['raw'])==r['answer']
            assert correct(r['answer'],case['gold'])==r['correct']
            assert (case['affected'] and correct(r['answer'],case['old_gold']))==r['stale']
            if not r['correct']:failures.append(dict(case=case['id'],arm=arm,answer=r['answer'],gold=case['gold'],support=r['support_hit'],call=r['answer_call']))
            if call['finish_reason']=='length':truncations.append(dict(case=case['id'],arm=arm,call=call['call_id']))
    check_saved(phase)
    hardware=list(map(json.loads,(path/'hardware.jsonl').read_text().splitlines()))
    result=dict(status='passed',requests=len(rows),saved_states=saved,physical_calls=len(calls),failures=failures,
                truncations=truncations,competing_samples=sum(bool(r['competing']) for r in hardware),
                score_support_note='Gold source IDs used only here and in post-ranking diagnostics.',
                source_revision=manifest['git_revision'])
    dump_json(path/'audit.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('failures','truncations')},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('path');p.add_argument('--previous',nargs='*',default=[]);a=p.parse_args();audit(a.path,a.previous)
