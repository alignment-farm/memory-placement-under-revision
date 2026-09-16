# Cost accounting and limits

The physical experiment executes every comparator, so its cost is not one
deployment's cost. `calls.jsonl` counts each physical generation once and keeps
its raw prompt/response, input/generated tokens, actual reused KV tokens, elapsed
time and peak allocation. Every attempted development and integrity run remains
in evidence, including unsuccessful preflights, prompting and a strict cache
prose-equivalence assertion. Model-loading and whole-run wall time are separate.

Each arm's result charges its actual queried pairs; observed-only is matched to
retained EARM's acquisitions without factor fitting. Changed-ID invalidation
charges mandatory extra cold starts. ALS time is measured excluding its scoring
callback, with iteration counts and matrix bytes. Index construction, content
revision and query ranking are timed. Full context pays no scorer or ALS but
does pay reference-prefix inference, completion and cache storage. Prefix keys
are hashes of actual text; changing text invalidates the affected prefix.
All arms can use the same cache capability. There are no repeated complete
requests within a deployed sequence and thus no answer-cache hits to exploit.

Common identical answer/scoring prompts across arms are executed once and their
generation is assigned to every consumer; the experimental saving is marked
explicitly. Arm time sums therefore reuse observations. They are not independently
measured end-to-end deployments: the physical runner interleaves arms and carries
its bounded cache pool through branches. Candidate score counts and raw tokens
are exact allocation quantities, while cache-hit timings reflect this execution
order. No wall-time crossover will be inferred from those sums. A deployment's
independent cache eviction pattern may differ. Model inference dominates the
measured local indexing/low-rank operations but is not replaced
with an artificial delay or dollar price.

One acquisition endpoint is copied into each counterfactual continuation. Per-
sequence lifetime tables add acquisition exactly once; summing all branches is
research cost, not a longer serial deployment. Content changes are ingested by
all arms; fixed cost and five branch preparations are not declared free simply
because text remains explicit. Revision validation is reported as audit work;
no answer repairs are made during fresh evaluation. Errors remain errors.

Existing pretrained model weights are shared across all arms and not trained by
this study. Their original pretraining cost is unknown and unallocated to every
arm equally. Local hash verification, loading, new score acquisition and cache
prefill are charged where measured. The researcher’s reading/implementation time,
source downloading and environment setup are disclosed but not converted into
model-call equivalents or a monetary repayment claim. Downloads/environments
are excluded from Git; model weights are reused read-only from the sibling.
