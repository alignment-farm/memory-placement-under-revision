"""Aggregate saved evidence; never makes model calls."""
import argparse
import collections
import json
from pathlib import Path
from statistics import mean

def analyze(path):
    path=Path(path)
    rows=[json.loads(s) for s in (path/'results.jsonl').read_text().splitlines()]
    calls={c['call_id']:c for c in map(json.loads,(path/'calls.jsonl').read_text().splitlines())}
    groups=collections.defaultdict(list)
    for r in rows:groups[r['case']['id'].rsplit('-',1)[0]].append(r)
    groups['all']=rows
    result={}
    for phase,rs in groups.items():
        arms={}
        for arm in rs[0]['answers']:
            vals=[r['answers'][arm] for r in rs]
            affected=[r['answers'][arm] for r in rs if r['case']['affected']]
            unaffected=[r['answers'][arm] for r in rs if not r['case']['affected']]
            arms[arm]=dict(n=len(vals),correct=sum(v['correct'] for v in vals),
                support_hits=sum(v['support_hit'] for v in vals),affected=len(affected),
                affected_correct=sum(v['correct'] for v in affected),stale=sum(v['stale'] for v in affected),
                unaffected_correct=sum(v['correct'] for v in unaffected),
                score_calls=sum(v['cost']['score_calls'] for v in vals),
                cold_extra=sum(v['cost'].get('cold_extra',0) for v in vals),
                score_seconds=sum(v['cost']['score_seconds'] for v in vals),
                answer_seconds=sum(v['answer_seconds'] for v in vals),
                learning_seconds=sum(v['cost'].get('learning_seconds',0) for v in vals),
                answer_prompt_tokens=sum(v['prompt_tokens'] for v in vals),
                answer_cached_tokens=sum(v['cached_tokens'] for v in vals),
                answer_completion_tokens=sum(v['completion_tokens'] for v in vals),
                imputed_contexts=sum(bool(v['imputed_selected']) for v in vals))
        diag={}
        for arm in ('retain','invalidate'):
            ds=[r['diagnostic'][arm] for r in rs if r['diagnostic'][arm]['unobserved_mse'] is not None]
            diag[arm]=dict(queries=len(ds),mse=mean(d['unobserved_mse'] for d in ds) if ds else None,
                          anchor_mean_mse=mean(d['anchor_mean_mse'] for d in ds) if ds else None,
                          unconverged=sum(not r['answers']['earm_'+arm]['cost']['fit_converged'] for r in rs))
        result[phase]=dict(arms=arms,diagnostic=diag)
    result['physical']=dict(calls=len(calls),seconds=sum(c['seconds'] for c in calls.values()),
                            prompt_tokens=sum(c['prompt_tokens'] for c in calls.values()),
                            cached_tokens=sum(c['cached_tokens'] for c in calls.values()),
                            completion_tokens=sum(c['completion_tokens'] for c in calls.values()),
                            peak_bytes=max(c['peak_bytes'] for c in calls.values()))
    # Per-sequence cumulative prefixes include acquisition once, never once per arm.
    result['lifetimes']={}
    for phase in groups:
        if phase in ('acquire','all'):continue
        sequence=groups['acquire']+groups[phase]
        result['lifetimes'][phase]={}
        for n in (4,8,12,16,20,24,28,32,36,40,48):
            if n>len(sequence):continue
            result['lifetimes'][phase][n]={a:dict(correct=sum(r['answers'][a]['correct'] for r in sequence[:n]),
                 score_calls=sum(r['answers'][a]['cost']['score_calls'] for r in sequence[:n]),
                 answer_prompt_tokens=sum(r['answers'][a]['prompt_tokens'] for r in sequence[:n]),
                 cached_tokens=sum(r['answers'][a]['cached_tokens'] for r in sequence[:n])) for a in sequence[0]['answers']}
    (path/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    for phase in groups:
        print(phase,{a:f"{v['correct']}/{v['n']} ({v['score_calls']} scores)" for a,v in result[phase]['arms'].items()})
    print('diagnostic',result['all']['diagnostic']);print('physical',result['physical'])
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('path');args=p.parse_args();analyze(args.path)
