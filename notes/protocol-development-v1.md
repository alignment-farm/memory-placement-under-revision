# Development protocol, 16 September 2026

Run the pinned EARM online core against twelve complete checking-account
documents. Explicitly adapted from the banking_knowledge release, not its
interactive task simulator. Four request families initially ask balance-waiver
or age-eligibility decisions for three fresh customers each. Sixteen initial
requests establish acquisition; five independent eight-request continuations
test stable reuse, narrow content revision, broad content revision, changed
evidence needs, and combined change. Three quarters of shifted requests ask
foreign ATM fees; the remainder retain the original family. These queries
require computation from rules rather than recalling a previously exposed answer.

Narrow revision changes Blue's waiver threshold $625 to $900 in every linked
statement of this bounded collection. Broad also changes Light Green's maximum
age 24 to 22 and Gold Years' minimum age 62 to 65. Out-of-scope corpus documents
are excluded for every treatment. No claim about updating the full bank corpus.
Selected documents have known unrelated inconsistencies (e.g. Light Green
purchase limits), so questions avoid those fields and withdrawal-limit conflicts.
Gold is computed from independently specified rules, never passed to a scorer,
answerer or learner. Release-note grading corrections were inspected.

EARM: rank 2, l2 .1, four-request blocks, actual budgets 12,6,4,3, half BM25
anchors and half author deterministic random anchors; 500 ALS iterations maximum.
This scales the author budget schedule to the small collection. Top K=2.
Compare retained identities and content-hash-triggered replacement of changed
identities (mandatory cold starts). No future family labels enter retrieval.
Controls: BM25, full pointwise reranking, all acquired observations ranked with
backfill, and full current context with actual native KV-prefix caching.
The model is native Qwen3-4B-Instruct-2507, verified against the sibling's pinned
hashes; no adapters are loaded. The initial served 27B calibration failed
relevance checks. Native direct-answer calibration failed a comparison; bounded
diagnosis found that a brief rule/comparison explanation repaired the two
opposite-sign probes. This reasoning prompt is frozen for development.

Only requested entries enter each online learner. Full comparator scores are
acquired afterward. Reused calls across arms are logged as experimental reuse;
each standalone arm is charged its acquisitions. Physical development inference
and deployment-equivalent counts are reported separately. Versioned text keys
invalidate KV prefixes; no artificial retrieval delays. CPU indexing, actual
score calls/tokens, ALS convergence/state size, answer tokens/times, revision
work and peak memory are retained. Timings are observational, not isolated.

Readiness requires useful complete quality, not just successful ALS updates.
Compare unobserved-score MSE with the current-anchor mean, retrieval support,
imputed selections and complete decisions. A failed learned contribution gets
at most two diagnostic adaptations on development, then a frozen fresh seed.
No final cases are used for method selection. The claim is restricted to fresh
numeric cases from these documented families, not unseen documents/domains.
