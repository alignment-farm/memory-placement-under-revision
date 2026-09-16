# Outcome interpretation after the frozen runs

The primary endpoint remains the predeclared exact three-value answer vector.
Do not replace it after inspecting explanations. Final auditing found one
correct vector unsupported by the supplied evidence: fresh-602,
content_broad-000, retained EARM. It retrieved only two Dark Green documents for
a Blue Account fee-waiver question. The answerer explicitly said it lacked the
rule, then returned [false,false,false], which happened to match the current
target. This is not evidence of successful use of the revised rule.

Report retained EARM as 120/128 under the frozen endpoint and 119/128 when a
correct vector must also have a known sufficient source in context. The latter
is a post hoc grounding diagnostic, not a replacement primary metric. The
source-supported variant does not change other arms' correct counts. Among ten
answer-changing requests, retention has nine exact vectors but only eight with
sufficient retrieved evidence. Invalidation has nine; the explicit controls ten.

Errors also differ in kind. Retention: seven truncated outputs and one missing-
support answer. Invalidation: six truncated outputs and one missing-support
answer. Observed-only: two truncations. Account-aware BM25: one truncation.
Full reranking: one incorrect computation with support. Full context: four
incorrect computations with support. No wrong vector exactly matches the old
policy's vector on an affected case; that absence does not imply all revised
requests succeeded.

Retained EARM has one paired primary win and seven losses against observed-only,
and one win/eight losses against account-aware BM25. Its lone win completes a
fee response within the token ceiling where the alternative contexts produce
truncation. This prevents interpreting the aggregate result as "imputation can
never help," but it does not provide aggregate acquisition-cost repayment.
