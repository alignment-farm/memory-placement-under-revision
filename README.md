# Memory placement under revision

**Completed 16 September 2026.** See [FINDINGS.md](FINDINGS.md) for the result:
account-aware lexical retrieval matched full reranking at 127/128 fresh requests,
while EARM did not demonstrate repayment against that cheap control. Development,
diagnosis and frozen fresh protocols are recorded under `notes/`; raw runs and
failed attempts are retained under `evidence/`. The original assignment follows.
This independent
ancillary study investigates when reuse repays the cost of learning a memory
component before consequential change. The investigator owns workload discovery,
methods, implementation, diagnostics, evidence and publication. A fresh ancillary
session can begin from this file and [AGENTS.md](AGENTS.md).

## Question and expectation

When an agent repeatedly uses a changing reference collection, which is worth
learning: its content, the procedure for retrieving evidence, or neither?

Compare useful performance and total cost over a sequence of requests and
revisions. The root expects that longer reuse can repay acquisition, whereas
frequent changes can remove the gain. A more specific expectation is that learned
retrieval can remain useful through some content changes if relevance remains
stable, but can lose that advantage when requests require different evidence.
Both expectations are untested here; no learned advantage is required.

Begin with one functioning published learned method, strong explicit controls,
and a bounded workload. The preferred first method is **EARM**, which learns
relevance relationships while records remain explicit. It is low-rank matrix
learning, not neural storage of document content. A result for EARM cannot settle
the value of weights or learned KV memory. Cartridges and Doc-to-LoRA are concrete
content-storage alternatives if a bounded feasibility investigation supports
including one; this is not an assignment to reproduce all three systems.

## Starting workload

Develop a versioned operational reference used by a stream of fresh requests.
The initial public lead is the document-based `banking_knowledge` domain in
[τ-bench at 2174a603f6d014ef94473ffa95957f6ce27100db](https://github.com/sierra-research/tau2-bench/tree/2174a603f6d014ef94473ffa95957f6ce27100db).
Its release contains product/procedure documents, tasks and source annotations.
Use it as a workload source, not as real financial guidance. Start with a coherent
bounded subset whose answers or decisions can be checked, rather than deploying
the entire conversational simulator. Such an adaptation is not a leaderboard
reproduction and does not establish complete conversational-agent performance.

A useful initial contrast has three conditions:

| Condition | Example of the intended change | What it distinguishes |
|---|---|---|
| Stable reference and request family | Fresh cases continue to use the same reference relations | Whether learning works and earns reuse benefit at all |
| Changed content, similar evidence needs | A documented eligibility condition changes; the same document remains relevant but some correct decisions change | Revision of content versus persistence of useful access experience |
| Changed evidence needs | Requests now depend on exceptions or procedures absent from the formerly useful subset | Whether retrieval experience remains helpful when relevance changes |

Cross content changes and changed evidence needs where useful, including a
combined condition. Use changes with actual answer consequences and retain
unaffected controls. This is a starting distinction, not a fixed experimental
matrix or a demand to construct a new benchmark.

Version the reference and update all linked statements and evaluation targets
affected by an edit. Confirm that some cases change and others should stay the
same. The author release notes record corrected policy/grading inconsistencies;
inspect selected cases rather than assuming all gold is valid. Ingest the same
visible changes for every method. Gold source annotations, gold decisions and
future requests belong to evaluation, not to a treatment's input.

Vary useful requests between revisions and the scope of revision. Retain real
retrieval costs, including cheap local indexing: do not add artificial delays or
withhold evidence to manufacture a learning advantage. Reuse must include fresh
cases, not only paraphrases of answers already revealed. Separate development
from evaluation by the dependencies relevant to the claim, including documents,
request families and revision sequences where applicable.

If this corpus does not support a discriminating, locally feasible comparison,
adapt the workload within the question. Explain why. Public alternatives include
LongMemEval's knowledge-update cases and StateMemBench's typed revisions, but a
single final question per history does not by itself measure repeated-use payoff.

## Methods and comparators

The root statically inspected the following releases; none was executed here.

| Method | Starting source | Preparation finding |
|---|---|---|
| EARM | [2608.22767v1](https://arxiv.org/html/2608.22767v1); [code ea06cb9](https://github.com/FengQi-HITSZ/earm/tree/ea06cb9059e9ebf7ebd9bf036ff08e188c18f6e0) | NumPy core; explicit online state and cold-start accounting. Adaptation to a new corpus must be identified. |
| Cartridges | [2506.06266v3](https://arxiv.org/html/2506.06266v3); [code ef34ba9](https://github.com/HazyResearch/cartridges/tree/ef34ba97a06049c34820506e2c283746284ae5f0) | Learned KV state; inspected attention implementation uses compiled FlexAttention. Apple execution not established. |
| Doc-to-LoRA | [2602.15902v1](https://arxiv.org/html/2602.15902v1); [code baa85db](https://github.com/SakanaAI/doc-to-lora/tree/baa85db4d5df9b29d618af432d6ebf28b3ad5a29) | Released hypernetwork checkpoints may avoid meta-training; CUDA/FlashAttention defaults and dependencies need feasibility work. |

For EARM, retaining an ID after changing its text retains old relevance experience
in the inspected runner. Assigning a new ID triggers cold-start scoring. Compare
retention with a sensible invalidation or reset policy; count re-learning rather
than treating replacement as free. Read the author reproduction guide: its live
path and replay of precomputed scores have different paid work. Local inference
models or first-stage retrieval may replace the author stack with explicit
provenance; do not call that exact reproduction.

Develop inexpensive lexical/semantic or structured retrieval suited to the data,
full reranking, and an observed-only control matched to the learned method's
score acquisitions. Include full or cached context for a tractable reference
subset, with actual cache reuse and invalidation if supported. A tool API that
does not expose caching is not evidence that cached context is intrinsically
expensive. Estimate unmeasured cache costs separately from measured outcomes.
Allow answer/score caching with version-aware invalidation where useful. Share
information, answerer and retrieval candidates when isolating the learned
component; document any necessary departures in whole-system comparisons.

Do not require every comparator at every scale. Establish that the closest cheap
alternative is competent and that the learned component has functioning
acquisition on development material. If it fails, pursue bounded diagnosis;
finite updates or a running pipeline do not establish successful learning.

## What the result should teach

Measure complete answer/decision quality, including stale answers and unaffected
cases, across the full sequence. Retrieval accuracy alone is diagnostic. Report
preparation, scoring, learning, serving, revision, validation and repair costs in
native units, alongside memory use. Show quality and costs together, not only
cost per success. Use actual cold-start counts and all attempted development
work. Distinguish deployment cost from research/development cost and disclose
allocation of any reused pretraining.

The useful output is a supported boundary: a reuse range where learning repays
cost at useful quality, a change that destroys or preserves it, or an explained
absence of payoff against a competent explicit alternative. If savings occur
only with full reranking as comparator while cheap retrieval performs as well,
that limits the payoff claim. An all-floor comparison requires acquisition
diagnosis; equal high accuracy can still be informative if costs differ.

## Relation to public and local work

[MemoryData, 2606.24775v1](https://arxiv.org/html/2606.24775v1) already compares
update robustness and operation costs. [StateMemBench, 2608.19652v1](https://arxiv.org/html/2608.19652v1)
provides structured revision and anti-update distinctions.
[Supersede, 2606.27472v1](https://arxiv.org/html/2606.27472v1) trains supersession
under a no-refeeding constraint. Their existence narrows our contribution to
learned-component lifetime with accessible evidence and competitive controls;
novelty remains to be checked as the design becomes concrete.

Construct-2's completed local studies establish conditional acquisition and
maintenance, but no acquisition-cost repayment at comparable complete quality.
This study addresses S5 and the placement of learning inside memory use. It is
independent of maintenance-predictor development and does not reopen completed
S1/S2/S4 phases. The [root direction](../../construct-2/notes/RESEARCH_DIRECTION.md)
and [source inspection](../../construct-2/sources/2026-09-16-study-preparation/README.md)
supply optional background; this README contains the starting assignment.

## Resources and publication

The preferred shared resource is the Mac Studio M1 with 64 GB unified memory,
serving models through Docker Model Runner over Tailscale. A native MLX gradient
route has worked in sibling studies; this does not establish compatibility for
these author implementations. Full details and coordination expectations are in
[AGENTS.md](AGENTS.md). No model, data download beyond static source inspection,
installation or experiment was launched during preparation.

Publish a local `FINDINGS.md` with the scientific conclusion, methods, limits,
reproduction instructions and identifiable code/evidence revisions. Keep failed
attempts and explain consequential design changes. The work can close on a
useful explanation, demonstrated limit or concrete resource constraint; neither
an immediate negative nor an indefinite search for a neural win is the goal.
