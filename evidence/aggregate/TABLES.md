# Fresh quality and cost tables

| Method | Complete requests | Score calls | Answer input tokens | Actual reused answer tokens | Answer output tokens | ALS seconds |
|---|---:|---:|---:|---:|---:|---:|
| earm_retain | 120/128 | 488 | 98843 | 60462 | 31906 | 1.233 |
| observed | 126/128 | 488 | 106242 | 67612 | 30644 | 0.000 |
| earm_invalidate | 121/128 | 509 | 98838 | 62153 | 31674 | 1.532 |
| bm25 | 127/128 | 0 | 109053 | 72051 | 30519 | 0.000 |
| full_rerank | 127/128 | 1536 | 103693 | 67060 | 30797 | 0.000 |
| full_context | 124/128 | 0 | 544033 | 492444 | 37857 | 0.000 |

Timings and cache hits are observations from the interleaved physical experiment,
not independent per-arm deployment benchmarks. See notes/cost-accounting.md.

| Phase | Retain | Invalidate | Observed | Lexical | Full rerank | Full context |
|---|---:|---:|---:|---:|---:|---:|
| acquire | 48/48 | 48/48 | 48/48 | 48/48 | 48/48 | 48/48 |
| stable | 16/16 | 16/16 | 16/16 | 16/16 | 16/16 | 16/16 |
| content_narrow | 16/16 | 15/16 | 16/16 | 16/16 | 16/16 | 16/16 |
| content_broad | 15/16 | 16/16 | 16/16 | 16/16 | 16/16 | 16/16 |
| evidence | 14/16 | 14/16 | 15/16 | 16/16 | 15/16 | 14/16 |
| combined | 11/16 | 12/16 | 15/16 | 15/16 | 16/16 | 14/16 |
| all | 120/128 | 121/128 | 126/128 | 127/128 | 127/128 | 124/128 |

## Allocated measured work

Includes scorer and answerer work; shared generations are assigned to each consumer.
These seconds are observations, not independently timed deployments.

| Method | Uncached input tokens | Output tokens | Allocated inference seconds | Index/revision seconds | Max EARM array bytes |
|---|---:|---:|---:|---:|---:|
| earm_retain | 77142 | 32988 | 752.173 | 0.018747 | 8064 |
| observed | 77391 | 31726 | 730.353 | 0.018747 | 0 |
| earm_invalidate | 81886 | 32796 | 755.594 | 0.018747 | 10224 |
| bm25 | 37002 | 30519 | 608.652 | 0.018747 | 0 |
| full_rerank | 145301 | 34081 | 973.567 | 0.018747 | 0 |
| full_context | 51589 | 37857 | 854.648 | 0.018747 | 0 |

## Imputation diagnostics

| Phase | EARM MSE | Historical row mean | Current anchor mean |
|---|---:|---:|---:|
| acquire | 0.1041 | 0.1014 | 0.2411 |
| stable | 0.0987 | 0.1363 | 0.2483 |
| content_narrow | 0.1007 | 0.1381 | 0.2859 |
| content_broad | 0.1133 | 0.1424 | 0.2737 |
| evidence | 0.2263 | 0.2283 | 0.2124 |
| combined | 0.2182 | 0.2208 | 0.2159 |
| all | 0.1357 | 0.1493 | 0.2452 |
