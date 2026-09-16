"""Independent assertions for consequences, causal masks and equal evidence."""
import json
import re
from pathlib import Path
from workload import documents, stream

seen=set()
for version in ('v0','narrow','broad'):
    docs=documents(version);by_id={d['id']:d for d in docs}
    assert len(docs)==12
    expected=(625 if version=='v0' else 900)
    for d in docs:
        if '_blue_account_' in d['id'] and d['id'].endswith(('001','002')):
            assert f'${expected}' in d['content']
            assert f'${900 if version=="v0" else 625}' not in d['content']
        if version=='broad' and '_light_green_account_' in d['id']:
            assert '13–24' not in d['content'] and '24 years' not in d['content']
        if version=='broad' and '_gold_years_account_' in d['id']:
            assert '62' not in d['content']
    cases=stream(921,80,version=version,seen=seen)
    assert all(set(c['supports'])<=by_id.keys() for c in cases)
    if version!='v0':
        assert any(c['affected'] for c in cases) and any(not c['affected'] for c in cases)
    for c in cases:
        if c['family']==0:
            balances=json.loads(re.search(r'\[[^\]]+\]',c['question']).group())
            threshold=int(re.search(r'minimum daily balance of \$(\d+)',by_id['doc_checking_accounts_blue_account_002']['content']).group(1))
            assert c['gold']==[b>=threshold for b in balances]
print('All linked threshold edits, consequence controls, source IDs and unique streams passed.')
