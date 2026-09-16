# Development decisions

Preflight v1 rejected a coincidentally duplicate three-age request; v2's hardware
guard mistook its own uv launcher for another experiment. Both stopped before
model work and are preserved. v3 is the first workload model run.

Interim diagnosis after 32 completed development requests: raw BM25 supports
28/32, mixed EARM 32/32, observed-only 31/32. Public account-name priority raises
the cheap control to 32/32, so the apparent gap versus raw BM25 is not a sufficient
learned-payoff result. Apply this same public priority to all retrieval arms.
Rank 8 lowers imputation MSE from .1121 to .0707 without changing mixed support;
under account-aware priorities, rank 2/8 MSE is .1019/.0704. These are interim
diagnostics, saved separately in diagnosis-v1, not final observations.

The model sometimes skipped the requested explanation and returned erroneous
booleans despite sufficient context. A bounded eight-case development diagnosis
will append an explicit request to show the rule and all three calculations.
It covers both prior failures and successes, including foreign-fee requests.
If adequate, use that same answer instruction in every final arm. No new model,
training objective or data source is introduced. Source and answer diagnostics
must finish before final seed generation.
