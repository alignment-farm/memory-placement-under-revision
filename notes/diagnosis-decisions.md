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

Completed diagnosis: account-aware ranking supplies support on 56/56 development
requests for mixed, observed-only and lexical; rank 8 reduces mixed unobserved
MSE to .1080 versus .1658 for rank 2. The reasoning-suffix check corrected all
substantive errors in eight probes but one hit the 320-token ceiling. Raising
the common ceiling to 512 produced eight parsed answers on the extended check.
One extended fee case exposed unspecified half-cent rounding: source policy
does not say how to round 2.5% of an odd dollar amount. Development's .011
numeric tolerance hid a one-cent difference. Preserve that evidence; final
cases use even dollar amounts for that family and an exact-cent tolerance of
1e-6. This removes ambiguity rather than declaring a bank rounding convention.
No further answerer/learner tuning is planned after the fresh protocol is frozen.
