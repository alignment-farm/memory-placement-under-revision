"""Separate-process equivalence and content-invalidation check."""
import json
from pathlib import Path
from runtime import Runtime,ANSWER_PREFIX,document_text,parse_answer
from workload import documents,dump_json

out=Path('evidence/cache-audit-v1');out.mkdir(exist_ok=False,parents=True)
rt=Runtime(out)
def prefix(v):return ANSWER_PREFIX+'\n\n'.join(document_text(d) for d in documents(v))
def query(balances):return f'For three separate Blue Account customers with minimum daily balances of {balances} dollars, is the monthly maintenance fee waived for each? Return booleans in the given order.\nShow the applicable numeric rule and all three calculations before your final JSON; do not skip them.'
a=rt.call('answer',prefix('v0'),query([650,850,950]),512)
b=rt.call('answer',prefix('v0'),query([660,860,960]),512)
rt.caches.clear();rt.dedup.clear()
c=rt.call('answer',prefix('v0'),query([660,860,960]),512)
d=rt.call('answer',prefix('narrow'),query([660,860,960]),512)
result=dict(warm_cached_tokens=b['cached_tokens'],cold_cached_tokens=c['cached_tokens'],
            identical_raw=b['raw']==c['raw'],identical_answers=parse_answer(b['raw'])==parse_answer(c['raw']),
            revised_cached_tokens=d['cached_tokens'],original=parse_answer(c['raw']),revised=parse_answer(d['raw']),
            revision_changes_answer=parse_answer(c['raw'])!=parse_answer(d['raw']),
            call_ids=[a['call_id'],b['call_id'],c['call_id'],d['call_id']])
dump_json(out/'summary.json',result)
print(json.dumps(result,indent=2))
assert result['warm_cached_tokens']>0 and result['cold_cached_tokens']==0
assert result['identical_answers'] and result['revised_cached_tokens']==0
assert result['original']==[True,True,True] and result['revised']==[False,False,True]
