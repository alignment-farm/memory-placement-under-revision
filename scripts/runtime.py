"""Measured native inference with real version-keyed KV-prefix reuse."""
import collections
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
import mlx.core as mx
from mlx_lm import load, stream_generate
from mlx_lm.models.cache import make_prompt_cache, trim_prompt_cache
from mlx_lm.sample_utils import make_sampler

MODEL=Path(__file__).resolve().parents[2]/"procedure-transfer/models/qwen3-4b-instruct"

class Runtime:
    def __init__(self,out):
        self.out=Path(out);self.log=self.out/'calls.jsonl';self.caches=collections.OrderedDict()
        self.dedup={};self.wait_seconds=0.;self.counter=0
        self.guard()
        mx.set_memory_limit(24*1024**3)
        t=time.monotonic();self.model,self.tok=load(str(MODEL));self.load_seconds=time.monotonic()-t

    def guard(self):
        while True:
            rows=subprocess.check_output(['ps','-axo','pid,command'],text=True).splitlines()
            competing=[r for r in rows if r.split()[0].isdigit() and int(r.split()[0]) not in (os.getpid(),os.getppid()) and 'python' in r.lower() and '.py' in r and
                       'memory-placement-under-revision' not in r and
                       any(s in r for s in ('experiment.py','train.py','maintenance_', 'scope_experiment','state_support'))]
            with (self.out/'hardware.jsonl').open('a') as f:
                f.write(json.dumps(dict(time=time.time(),competing=competing))+ '\n')
            if not competing:return
            print('Waiting for competing model job',competing,flush=True)
            t=time.monotonic();time.sleep(5);self.wait_seconds+=time.monotonic()-t

    def call(self,kind,prefix,question,limit):
        self.guard()
        prompt=prefix+'\n\nREQUEST:\n'+question
        key=hashlib.sha256((kind+'\0'+prefix).encode()).hexdigest()
        exact=hashlib.sha256(prompt.encode()).hexdigest()
        if exact in self.dedup:
            return dict(self.dedup[exact], experimental_reuse=True)
        t=time.monotonic()
        ids=self.tok.apply_chat_template([dict(role='user',content=prompt)],tokenize=True,add_generation_prompt=True,enable_thinking=False)
        reused=0
        if key in self.caches:
            previous,cache=self.caches.pop(key)
            for a,b in zip(previous,ids):
                if a!=b:break
                reused+=1
            reused=min(reused,len(ids)-1)
            trim_prompt_cache(cache,cache[0].offset-reused)
            assert cache[0].offset==reused
        else:cache=make_prompt_cache(self.model)
        raw='';last=None
        for piece in stream_generate(self.model,self.tok,prompt=ids[reused:],max_tokens=limit,
                                     prompt_cache=cache,sampler=make_sampler(temp=0)):
            raw+=piece.text;last=piece
        self.caches[key]=(ids,cache)
        while len(self.caches)>24:self.caches.popitem(last=False)
        row=dict(call_id=self.counter,kind=kind,prompt=prompt,raw=raw,seconds=time.monotonic()-t,
                 prompt_tokens=len(ids),cached_tokens=reused,completion_tokens=last.generation_tokens,
                 finish_reason=last.finish_reason,peak_bytes=mx.get_peak_memory(),
                 kv_bytes=sum(sum(c.nbytes for c in kv) for _,kv in self.caches.values()),experimental_reuse=False)
        self.counter+=1
        with self.log.open('a') as f:f.write(json.dumps(row)+'\n')
        self.dedup[exact]=row
        return row

SCORE_PREFIX='''Rate whether the reference document provides evidence needed to answer the request.
Output only one number: 0 = unrelated; 0.5 = partially useful; 1 = directly useful.
Do not decide the customer's outcome. Score usefulness of the evidence.
REFERENCE DOCUMENT:\n'''
ANSWER_PREFIX='''Answer the request using only the current reference documents below.
First identify the applicable rule and briefly compute each comparison or fee.
Finish with a JSON object with key "answers" containing exactly three values in request order.
Use JSON booleans for eligibility/waivers, numbers for fees, or null if evidence is missing.
REFERENCE DOCUMENTS:\n'''

def document_text(d):return d['id']+'\n'+d['title']+'\n'+d['content']

def parse_answer(raw):
    decoder=json.JSONDecoder();parsed=None
    for i,c in enumerate(raw):
        if c=='{':
            try:
                obj,_=decoder.raw_decode(raw[i:])
                if isinstance(obj,dict) and isinstance(obj.get('answers'),list):parsed=obj['answers']
            except (ValueError,TypeError):pass
    return parsed
