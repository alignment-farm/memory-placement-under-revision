import json, time
from pathlib import Path
import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

mx.set_memory_limit(24*1024**3)
model,tok=load(str(Path('../procedure-transfer/models/qwen3-4b-instruct').resolve()))
prompts=[
 'What is 2 + 2?',
 'Is 700 greater than or equal to 625? Explain your comparison.',
 'Document: Blue Account fee waiver requires a minimum daily balance of $625. Customer minimum daily balance: $700. First compare the balance with the threshold, then decide whether the fee is waived. Explain briefly and finish with JSON {"waived": true} or {"waived": false}.',
 'Document: Blue Account fee waiver requires a minimum daily balance of $625. Customer minimum daily balance: $500. First compare the balance with the threshold, then decide whether the fee is waived. Explain briefly and finish with JSON {"waived": true} or {"waived": false}.',
]
rows=[]
for p in prompts:
 t=time.monotonic()
 ids=tok.apply_chat_template([dict(role='user',content=p)],add_generation_prompt=True,enable_thinking=False)
 a=generate(model,tok,prompt=ids,max_tokens=192,sampler=make_sampler(temp=0),verbose=False)
 rows.append(dict(prompt=p,answer=a,seconds=time.monotonic()-t));print(rows[-1],flush=True)
Path('evidence/calibration-v1/diagnosis.json').write_text(json.dumps(rows,indent=2))
