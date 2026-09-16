# Frozen fresh evaluation

Freeze after development and bounded diagnosis, before generating the cases.
Use the unmodified author EARM online core with rank 8, l2 .1, block size 4,
budgets 12/6/4/3 and maximum 500 ALS iterations. Give all retrieval arms the same
account-aware BM25 scores. Account priority is derived from visible document IDs
and the longest account name in the request; it does not use task annotations.
K=2, the same native Qwen answerer, the explicit-calculation suffix, and a common
512-token ceiling. Grade the complete three-value vector, booleans exactly and
dollar fees within 1e-6. Dark Green withdrawal amounts are even dollars, so all
fees are exactly representable in cents without inventing a half-cent rule.

Two independent streams: seed 601 with 16 acquisition requests and seed 602 with
32, each followed by five separate eight-request continuations. Total 128
requests / 384 elementary decisions, six arms. Each branch starts from a copy
of its own acquisition endpoint. Acquisition costs are paid once per deployed
sequence; all branches' experimental costs are retained. The 16-versus-32 reuse
comparison is descriptive across seeds, not a paired causal estimate. Report
cumulative prefixes and full quality/cost curves without extrapolating a win.

Generate seed 601 excluding every development request; generate seed 602
excluding development and seed 601 requests. The exclusion checks only string
identity, never gold or performance. Repeated documents and request families
are intentional: generalization is to fresh numerical instances and sequences,
not to new policies, documents or language families. No treatment sees future
requests, expected values, or gold source IDs. Different branch conditions use
different fresh cases; changed-case targets are checked against v0 counterfactuals.

Compare retention and hash-triggered changed-document ID replacement. Other
controls: all scored observations with backfill, account-aware lexical, full
pointwise reranking and full current context with measured KV reuse. Full
comparator scores are acquired only after the learners finish each request.
All visible text changes propagate to every method at the same boundary.

Primary endpoint: complete-vector correctness, separately for affected,
unaffected and evidence-shift cases, with old-policy-consistent wrong answers
reported. Secondary: support coverage, imputation error and contribution beyond
observed-only, all scored pairs, actual prompt/completion/cache tokens, measured
fit and index/revision costs, and memory. Do not treat retrieval support or
finite updates as proof of useful learning. A score-count advantage over full
reranking does not establish repayment versus lexical or observed-only.

No method changes will use fresh outcomes. Only execution-integrity repairs
may trigger a recorded rerun. Any remaining answerer errors are final errors.
Following fresh execution, audit saved state, costs, request separation and
document revision consequences; publish FINDINGS.md and Git revisions locally.
