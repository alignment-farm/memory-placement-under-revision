"""Feasibility/calibration only; no workload gold enters either model."""
import hashlib
import json
import subprocess
import time
import urllib.request
from pathlib import Path

OUT = Path("evidence/calibration-v1")
OUT.mkdir(parents=True, exist_ok=True)
MODEL = Path("../procedure-transfer/models/qwen3-4b-instruct").resolve()
ref = json.loads(Path("../procedure-transfer/sources/model-reference.json").read_text())
t = time.monotonic()
for name, digest in ref["files"].items():
    with (MODEL / name).open("rb") as f:
        assert hashlib.file_digest(f, "sha256").hexdigest() == digest
(OUT / "model.json").write_text(json.dumps({"path": str(MODEL), "revision": "cdbee75f17c01a7cc42f958dc650907174af0554", "hashes": ref["files"], "verification_seconds": time.monotonic()-t}, indent=2))
(OUT / "processes.txt").write_text(subprocess.check_output(["ps", "-axo", "pid,pcpu,pmem,command"], text=True))
import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler
mx.set_memory_limit(24 * 1024**3)
start=time.monotonic()
model, tok = load(str(MODEL))
prompts = [
    "Rate whether the document provides evidence needed to answer the question. Output only a number: 0 = unrelated, 0.5 = partially useful, 1 = directly answers. Question: Is the Blue Account monthly fee waived for a minimum daily balance of $700? Document: Blue Account fee waiver requires a minimum daily balance of $625. Score:",
    "Rate whether the document provides evidence needed to answer the question. Output only a number: 0 = unrelated, 0.5 = partially useful, 1 = directly answers. Question: Is the Blue Account monthly fee waived for a minimum daily balance of $700? Document: Purple Account includes six airport lounge visits each year. Score:",
    'Use only the document. Return JSON with key "answer". Question: Is the Blue Account monthly fee waived for a minimum daily balance of $700? Document: Blue Account fee waiver requires a minimum daily balance of $625.',
]
rows=[]
for prompt in prompts:
    tick=time.monotonic()
    text=tok.apply_chat_template([{"role":"user","content":prompt}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    answer=generate(model,tok,prompt=text,max_tokens=64,sampler=make_sampler(temp=0),verbose=False)
    rows.append(dict(prompt=prompt,answer=answer,seconds=time.monotonic()-tick))
    print(rows[-1],flush=True)
(OUT / "native.json").write_text(json.dumps({"rows":rows,"seconds":time.monotonic()-start,"peak_bytes":mx.get_peak_memory()},indent=2))
