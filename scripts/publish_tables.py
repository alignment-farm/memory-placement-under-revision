"""Produce compact reproducible quality/cost tables after both fresh runs finish."""
import collections
import copy
import json
import time
from pathlib import Path
from statistics import mean
from analyze import analyze
from workload import dump_json

paths=[Path('evidence/fresh-601'),Path('evidence/fresh-602')]
assert all(json.loads((p/'summary.json').read_text())['status']=='complete' for p in paths)
analyses=[analyze(p) for p in paths]
allrows=[];allcalls=[];errors=[]
for path in paths:
    rows=list(map(json.loads,(path/'results.jsonl').read_text().splitlines()))
    calls=list(map(json.loads,(path/'calls.jsonl').read_text().splitlines()))
    by_call={c['call_id']:c for c in calls}
    allrows+=rows;allcalls+=calls
    for row in rows:
        for arm,r in row['answers'].items():
            if not r['correct']:
                call=by_call[r['answer_call']]
                kind='truncated' if call['finish_reason']=='length' else 'missing_support' if not r['support_hit'] else 'wrong_with_support'
                errors.append(dict(run=path.name,case=row['case']['id'],arm=arm,kind=kind,affected=row['case']['affected'],stale=r['stale'],call=call['call_id']))
arms=list(allrows[0]['answers'])
aggregate={}
for phase in analyses[0]:
    if phase in ('physical','lifetimes'):continue
    aggregate[phase]={}
    for arm in arms:
        a,b=[x[phase]['arms'][arm] for x in analyses]
        aggregate[phase][arm]={k:(max(a[k],b[k]) if k=='max_model_bytes' else a[k]+b[k]) for k in a}

def contrast(a,b):
    return dict(a_only=sum(r['answers'][a]['correct'] and not r['answers'][b]['correct'] for r in allrows),
                b_only=sum(r['answers'][b]['correct'] and not r['answers'][a]['correct'] for r in allrows),
                same=sum(r['answers'][a]['correct']==r['answers'][b]['correct'] for r in allrows))

# Historical mean baseline: exactly the same acquired observations as retention.
rowmean=[]
for path in paths:
    rows=list(map(json.loads,(path/'results.jsonl').read_text().splitlines()))
    history=collections.defaultdict(list);acquired=None;phase='acquire'
    for row in rows:
        now=row['case']['id'].rsplit('-',1)[0]
        if now!=phase:
            if phase=='acquire':acquired=copy.deepcopy(history)
            history=copy.deepcopy(acquired);phase=now
        observed=row['diagnostic']['retain']['observed'];unseen=set(row['scores'])-set(observed)
        if unseen:
            rowmean.append(dict(run=path.name,phase=phase,case=row['case']['id'],
                historical_rowmean_mse=mean((mean(history[m])-row['scores'][m])**2 for m in unseen),
                earm_mse=row['diagnostic']['retain']['unobserved_mse'],
                anchor_mean_mse=row['diagnostic']['retain']['anchor_mean_mse']))
        for m in observed:history[m].append(row['scores'][m])

diag={phase:{key:mean(r[key] for r in rowmean if phase=='all' or r['phase']==phase)
             for key in ('earm_mse','historical_rowmean_mse','anchor_mean_mse')}
      for phase in aggregate}
research=[]
for p in sorted(Path('evidence').glob('*/calls.jsonl')):
    cs=list(map(json.loads,p.read_text().splitlines()))
    research.append(dict(run=p.parent.name,calls=len(cs),seconds=sum(c['seconds'] for c in cs),
                        prompt_tokens=sum(c['prompt_tokens'] for c in cs),cached_tokens=sum(c['cached_tokens'] for c in cs),
                        completion_tokens=sum(c['completion_tokens'] for c in cs),peak_bytes=max(c['peak_bytes'] for c in cs)))
result=dict(quality_cost=aggregate,contrast_observed=contrast('earm_retain','observed'),
            contrast_lexical=contrast('earm_retain','bm25'),imputation_diagnostics=diag,
            physical_research=research,final_wall_seconds=sum(json.loads((p/'summary.json').read_text())['seconds'] for p in paths),
            final_peak_bytes=max(c['peak_bytes'] for c in allcalls),rowmean_records=rowmean)
result['errors']=errors
result['supported_correct']={a:sum(r['answers'][a]['correct'] and r['answers'][a]['support_hit'] for r in allrows) for a in arms}
result['unsupported_correct']=[dict(run=p.name,case=r['case']['id'],arm=a,call=v['answer_call'])
                               for p in paths for r in map(json.loads,(p/'results.jsonl').read_text().splitlines())
                               for a,v in r['answers'].items() if v['correct'] and not v['support_hit']]
cal=Path('evidence/calibration-v1')
native=json.loads((cal/'native.json').read_text())['rows']+json.loads((cal/'diagnosis.json').read_text())
served=json.loads((cal/'served-probes.json').read_text())['probes']
result['calibration']=dict(native_calls=len(native),native_generation_seconds=sum(c['seconds'] for c in native),
                           served_calls=len(served),served_reported_seconds=sum(c['prompt_ms']+c['predicted_ms'] for c in served)/1000,
                           hash_verification_seconds=json.loads((cal/'model.json').read_text())['verification_seconds'])
out=Path('evidence/aggregate');out.mkdir(exist_ok=True);dump_json(out/'summary.json',result)
lines=['# Fresh quality and cost tables','',
       '| Method | Complete requests | Score calls | Answer input tokens | Actual reused answer tokens | Answer output tokens | ALS seconds |',
       '|---|---:|---:|---:|---:|---:|---:|']
for arm,r in aggregate['all'].items():
    lines.append(f"| {arm} | {r['correct']}/{r['n']} | {r['score_calls']} | {r['answer_prompt_tokens']} | {r['answer_cached_tokens']} | {r['answer_completion_tokens']} | {r['learning_seconds']:.3f} |")
lines+=['','Timings and cache hits are observations from the interleaved physical experiment,','not independent per-arm deployment benchmarks. See notes/cost-accounting.md.','',
        '| Phase | Retain | Invalidate | Observed | Lexical | Full rerank | Full context |','|---|---:|---:|---:|---:|---:|---:|']
for phase,arms_data in aggregate.items():
    lines.append('| '+phase+' | '+' | '.join(f"{arms_data[a]['correct']}/{arms_data[a]['n']}" for a in ['earm_retain','earm_invalidate','observed','bm25','full_rerank','full_context'])+' |')
lines+=['','## Allocated measured work','',
        'Includes scorer and answerer work; shared generations are assigned to each consumer.',
        'These seconds are observations, not independently timed deployments.','',
        '| Method | Uncached input tokens | Output tokens | Allocated inference seconds | Index/revision seconds | Max EARM array bytes |',
        '|---|---:|---:|---:|---:|---:|']
for arm,r in aggregate['all'].items():
    uncached=r['score_prompt_tokens']-r['score_cached_tokens']+r['answer_prompt_tokens']-r['answer_cached_tokens']
    output=r['score_completion_tokens']+r['answer_completion_tokens']
    lines.append(f"| {arm} | {uncached} | {output} | {r['score_seconds']+r['answer_seconds']:.3f} | {r['index_revision_seconds']:.6f} | {r['max_model_bytes']} |")
lines+=['','## Imputation diagnostics','', '| Phase | EARM MSE | Historical row mean | Current anchor mean |','|---|---:|---:|---:|']
for phase,ds in diag.items():lines.append(f"| {phase} | {ds['earm_mse']:.4f} | {ds['historical_rowmean_mse']:.4f} | {ds['anchor_mean_mse']:.4f} |")
(out/'TABLES.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('quality_cost','physical_research','rowmean_records')},indent=2))
