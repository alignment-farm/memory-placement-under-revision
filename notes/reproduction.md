# Reproduction

All commands run from this study root. Python is managed by `uv`; `uv.lock`
pins the native environment, including MLX-LM commit
86b48c461feebf87c58788655b7e57b5574b9e6d. No Docker/Compose service installation
was needed. `sh scripts/reproduce.sh` obtains the pinned author/data checkouts
and installs the environment without fetching any model weights.

The native runner reads the existing sibling path
`../procedure-transfer/models/qwen3-4b-instruct`. For reproduction in a new
workspace, place Qwen/Qwen3-4B-Instruct-2507 revision
cdbee75f17c01a7cc42f958dc650907174af0554 at that relative location, or adapt only
the path in scripts/runtime.py. Check all hashes against
evidence/calibration-v1/model.json before loading. No trained adapters are used.
Do not reuse a result directory: runners fail if it already exists, preserving
prior runs. The helper shell checks out pinned commits only inside downloads/;
use pristine download checkouts if you have modified author code there.

Fresh protocol source was frozen at bb5d737 and the guard-only correction at
661fedf. Every run records its exact Git revision, arguments and status in its
manifest. These are the fresh execution commands (choose unused output paths
to rerun; change the second exclusion path accordingly):

```sh
uv run python scripts/experiment.py --output evidence/fresh-601 --seed 601 --initial 16 --after 8 --rank 8 --entity --explain --exclude evidence/development-v3/evaluation-only.json
uv run python scripts/experiment.py --output evidence/fresh-602 --seed 602 --initial 32 --after 8 --rank 8 --entity --explain --exclude evidence/development-v3/evaluation-only.json evidence/fresh-601/evaluation-only.json
```

Regenerate reports and audit completed evidence without model inference:

```sh
uv run python scripts/check_workload.py
uv run python scripts/audit_evidence.py evidence/fresh-601 --previous evidence/development-v3/evaluation-only.json
uv run python scripts/audit_evidence.py evidence/fresh-602 --previous evidence/development-v3/evaluation-only.json evidence/fresh-601/evaluation-only.json
uv run python scripts/publish_tables.py
```

The source-target auditor independently extracts numeric rules from the saved
current documents. It reconstructs masked EARM updates using only acquired
observations, compares every saved state, verifies actual cold starts and checks
all prompt/response/cost references. It also checks request separation and exact
complete-vector scoring. It does not use new generations to repair final errors.

To reproduce development from its original source, check out the run's recorded
revision in a separate study checkout. Later revisions intentionally repair
prompting, the cheap lexical control, rounding ambiguity, duplicate sampling and
guard behavior; running current code with the old arguments is not a byte-exact
reproduction of those earlier attempts. The raw failed and successful evidence
remains available for inspection.

Generation is temperature zero but cached and cold prefill can produce different
prose on MLX. A separate four-call audit checked decision equivalence and actual
content invalidation; it is not a proof of universal bitwise determinism.
