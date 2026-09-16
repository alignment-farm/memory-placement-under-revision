# Cache audit interpretation

The original auditor required identical generated prose and failed that assertion.
The cached and cold answers are identical and correct; explanations differ in
wording. This is not bitwise generation equivalence. Trimming and reuse preserved
the complete tested decision, with 4,182 tokens reused versus zero cold tokens.
The revised text gets a new key, reuses zero tokens, and changes the complete
answer from [true,true,true] to [false,false,true], as required.

The auditor's future assertion checks complete answer equivalence, not prose
identity. Original calls, summary and the fact of the failed stricter assertion
are preserved here. This is a four-call integrity check, not a general claim
that cache state never influences generation. Cross-arm identical prompts are
experimentally shared; reported times are not independent per-arm benchmarks.
