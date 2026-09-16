# Explicit access beats learned reranking on this bounded revision workload

Completed 16 September 2026. **No repayment of learned access was demonstrated
against a competent cheap alternative.** Account-aware BM25 answered 127/128
fresh requests correctly, matching full reranking without its scoring calls.
EARM's retained-ID and invalidated-ID variants answered 120/128 and 121/128.
Learning improved some relevance-score predictions, but not complete answer
quality or recorded inference work relative to the cheap control.

This is a local boundary result for twelve named-account reference documents,
not a claim that learned retrieval never helps. EARM learns access relationships;
this study does not test learned document content, Cartridges or Doc-to-LoRA.

## Result and its scope

Each request requires three decisions or fee calculations. The primary endpoint
is the **entire requested three-value vector**, with strict boolean/numeric
checking. Two disjoint fresh streams contain 128 requests, or 384 elementary
decisions. All six methods face the same requests and current document text.

| Method | Exact answer vectors | Scored query–document pairs | Correct on 10 answer-changing requests |
|---|---:|---:|---:|
| Account-aware BM25 | 127/128 | 0 | 10/10 |
| Full pointwise reranking | 127/128 | 1,536 | 10/10 |
| All acquired observations, without completion | 126/128 | 488 | 10/10 |
| Full current context, with actual KV reuse | 124/128 | 0 | 10/10 |
| EARM, retain document IDs | 120/128 | 488 | 9/10 |
| EARM, replace changed document IDs | 121/128 | 509 | 9/10 |

These pooled counts include each acquisition stream once and its five
counterfactual continuations. They are not one 128-request serial deployment.
The [full tables](evidence/aggregate/TABLES.md) include each condition and native
cost units; [machine-readable aggregates](evidence/aggregate/summary.json) retain
paired contrasts and individual errors.

The cheap control derives account names from public document IDs and prioritizes
the longest account name mentioned in the request before BM25 ordering. It sees
no gold source annotations. EARM receives those same priorities and the same
candidate pool. With this visible structure, inexpensive retrieval already
supplies sufficient evidence on every fresh request. Its one failure is an
output truncation, not a retrieval miss.

Retained EARM has one paired win and eight losses against this control, and one
win/seven losses against observed-only. Its one win completes a response within
the common output budget when the other selected contexts induce truncation.
Thus completion can help an individual response, but these observations do not
show aggregate acquisition-cost repayment.

There is also a scoring limitation: one of EARM's 120 correct vectors is an
unsupported all-false answer. On fresh-602/content_broad-000 it retrieved Dark
Green documents for a Blue Account question, admitted the missing rule, and
nevertheless returned the coincidentally correct values. Requiring both a
correct vector and a known sufficient source gives **119/128** for retention;
the other arms' counts do not change. This is a post hoc grounding diagnostic,
not a replacement primary endpoint. See the [outcome audit](notes/outcome-audit.md).

## Reuse, revision and acquisition

The two acquisition lengths are 16 and 32 requests. Each learned endpoint is
copied into five eight-request continuations: stable reuse, narrow content
change, broad content change, changed evidence needs, and combined changes.
Every fourth request in a shifted continuation remains in an original family.

Stable 24-request lifetimes use 124 EARM scoring calls versus 288 for full
reranking; stable 40-request lifetimes use 172 versus 480. All methods answer
those stable sequences correctly. These are 56.9% and 64.2% scoring reductions
against full reranking, **not repayment against lexical retrieval**, which uses
zero scoring calls. Different seeds accompany the two lengths, so their
difference is descriptive rather than a paired causal effect of longer reuse.

The revisions change Blue's fee-waiver balance from $625 to $900; the broad
revision additionally changes Light Green's maximum age from 24 to 22 and Gold
Years' minimum age from 62 to 65. Every linked statement in the bounded collection
is edited. The evidence-shift requests ask foreign ATM fees, including minima,
caps, tiers and a balance-dependent waiver. All candidates were already visible;
no future-relevant document was withheld from a control.

Ten fresh request targets actually change under the content revisions. No wrong
answer vector matches the obsolete target on those cases, but each EARM variant
misses one because it selects insufficient evidence. Zero stale answers is
therefore not equivalent to successful revision. Retention additionally has the
unsupported correct vector described above.

The sampled combined branches have **zero answer-changing targets**: documents
are revised, but the sampled decisions are unaffected. They are retained without
selective regeneration. They cannot establish robustness to consequential
content and relevance changes in the same answer. This limitation and the
unaffected controls are explicit in [the interpretation record](notes/fresh-interpretation-limits.md).

Acquisition was diagnosed rather than inferred from finite updates. Under stable
reuse, retained EARM's missing-score MSE is 0.0987 versus 0.1363 for a historical
row mean using exactly the same acquired observations. Under narrow/broad edits
it is 0.1007/0.1133 versus 0.1381/0.1424. Under changed evidence needs it rises to
0.2263, essentially matching the historical mean's 0.2283 and trailing the
current-anchor mean's 0.2124. These are predictions of the **model scorer's
ratings**, not ground-truth relevance or answer correctness. Improved prediction
in stable settings did not add useful complete quality beyond competent access.

## What failed

Retained EARM's eight primary failures comprise seven truncated outputs and one
missing-support answer; invalidation has six truncations and one missing-support
answer. Observed-only has two truncations, lexical retrieval one. Full reranking
has one incorrect computation despite support; full context has four.

Two traces explain why retrieval metrics alone are inadequate:

- In fresh-602/content_broad-004, the sufficient Blue summary receives a real
  score of 0.5. EARM assigns unrelated Dark Green and Light Green documents
  completed scores of approximately 0.575 and 0.514, displacing the evidence.
  Observed-only keeps the sufficient document and answers the revised rule.
- In several fee cases, completion adds an irrelevant account's waiver policy.
  The answerer correctly distinguishes the accounts but spends its 512-token
  budget explaining the distinction and fails to finish the required JSON.
  Other full-context errors explicitly turn a maximum fee into a minimum.

These errors are preserved. No fresh answer was repaired or rerun for a better
score. Retaining identities saves 21 cold-start acquisitions across the pooled
protocol, but invalidation is neither uniformly better nor uniformly worse.

## Methods, costs and provenance

The study uses the unchanged online core of
[EARM](https://arxiv.org/html/2608.22767v1), code revision
`ea06cb9059e9ebf7ebd9bf036ff08e188c18f6e0`. Adaptations are explicit banking
records instead of Mem0/LoCoMo, account-aware BM25 priorities, rank 8, four-query
blocks with budgets 12/6/4/3, l2 0.1 and a 500-iteration ALS ceiling. All fresh fits
converged. Changed-ID invalidation replaces only records whose content hashes
change. Observed-only ranks **all** acquired observations with backfill to K=2,
stronger than filtering only the observed items inside EARM's selected context.

The twelve complete documents come from `banking_knowledge` in
[tau2-bench](https://github.com/sierra-research/tau2-bench/tree/2174a603f6d014ef94473ffa95957f6ce27100db),
pinned at `2174a603f6d014ef94473ffa95957f6ce27100db`. Release-note policy/grading
corrections were inspected. New numeric cases avoid unrelated document
inconsistencies and unspecified half-cent rounding. This is not a conversational
simulator or leaderboard reproduction. Generalization is to fresh numeric
instances and sequences, not new documents, request families or domains.

Scoring and answering use native Qwen3-4B-Instruct-2507 revision
`cdbee75f17c01a7cc42f958dc650907174af0554`, with hash-verified existing weights and
no adapters. The preferred served 27B route failed two preliminary relevance
probes; the native route and all prompt failures are retained. Source and runtime
provenance appear in [sources/README.md](sources/README.md) and `uv.lock`.

Recorded scorer-plus-answer work favors the cheap control: retained EARM uses
77,142 uncached input tokens and 32,988 output tokens versus BM25's 37,002 and
30,519. Their allocated inference times are 752.2 and 608.7 seconds. EARM fitting
adds 1.23 seconds; its largest recorded arrays occupy 8,064 bytes. Shared index
construction/revision totals 18.7 ms and query ranking 42.6 ms. The full-context
arm actually reuses 492,444 of 544,033 answer-input tokens; caching is not assumed
unavailable or charged as repeated cold prefill.

Those per-arm time/token allocations come from an interleaved experiment that
shares identical generations and carries a bounded cache pool through branches.
They are **not independent deployment timing benchmarks**. Counts, raw prompts,
actual cache hits and native times remain available; no dollar, energy or
wall-time crossover is inferred. See [cost accounting](notes/cost-accounting.md).

Fresh execution made 1,936 physical model calls and took 2,732.9 seconds
(45.55 minutes), with no observed competing Python model jobs or genuine resource
waits. Peak MLX allocation was 13,339,611,224 bytes. Across retained development,
diagnosis, cache audit and fresh runs, there were 2,814 native calls, plus two
served calibration calls. Recorded native generation time totals 3,075.0 seconds.
The model hash check took 3.98 seconds. Human research/implementation time,
source/environment setup and original model pretraining are unpriced, not free;
the common pretrained weights are allocated equally to all arms.

The initial development run had low complete quality; bounded diagnosis improved
the lexical control, compared ranks 2/8 and repaired the answer instruction.
Preflight duplicate/guard failures, a truncated diagnostic response and the
failed stricter cache-prose assertion remain in evidence. Cached and cold audit
answers agree and revision invalidation works, but generated prose is not
bitwise identical. [Development decisions](notes/diagnosis-decisions.md) and the
[frozen fresh protocol](notes/protocol-fresh-v1.md) record selection before fresh
generation. Related public work already studies update cost and evolving state;
no broad novelty claim is made here.

## Verification and reproduction

The author's 21 matrix-completion/online tests passed. Independent audits checked
all 128 targets against saved document text, every scorer/answer prompt, acquired
cell masks, cold-start counts, request separation and all 24 saved learner states.
Both [fresh-601](evidence/fresh-601/audit.json) and
[fresh-602](evidence/fresh-602/audit.json) passed. Audits do not revise the frozen
endpoint or turn unsupported answers into grounded successes.

Experimental source revisions are `661fedfdd06d6232789d36f791eb0056d1669aff`
and `8ce3332790688ea7a18d7fd95e7c5a4066b04f8d`; their treatment code is the same.
Frozen protocol: `bb5d737`. Completed evidence, aggregates and outcome caveats:
**`be3594a`**. Every run also contains its arguments and source revision.

Follow [reproduction instructions](notes/reproduction.md) to obtain pinned
sources, verify the existing model and rerun into unused output directories.
`uv run python scripts/publish_tables.py` regenerates the aggregate tables from
saved evidence without inference. All study-owned model jobs have ended; no
root or sibling study files were changed.
