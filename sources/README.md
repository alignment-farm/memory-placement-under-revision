# Pinned starting sources

- EARM: FengQi-HITSZ/earm, ea06cb9059e9ebf7ebd9bf036ff08e188c18f6e0,
  https://arxiv.org/html/2608.22767v1. Read README, reproduction guide,
  online state and observed-only implementation. Use its actual online core.
- Workload: sierra-research/tau2-bench,
  2174a603f6d014ef94473ffa95957f6ce27100db, banking_knowledge.

Source checkouts live under ignored downloads/. Research downloads are not
experimental evidence. The first arXiv query API attempt was serial, with a
descriptive User-Agent, and returned `Rate exceeded.`; preserved in
arxiv-metadata.xml. HTML paper access succeeded. Metadata will be retried with
spacing; no parallel API/OAI requests are used.

The adaptation replaces Mem0/LoCoMo with explicit banking documents and BM25
candidate priorities. It is not a paper or conversational leaderboard reproduction.
EARM learns access scores, not the contents of documents. Observed-only will rank
all acquired scores with backfill up to K, stronger than the author ablation's
filtering of only the mixed Top-K without backfill. All arms see current text.

## Execution inspection

EARM v1 HTML was read, especially the causal low-rank objective, fixed budget
schedule, and limitations on heterogeneous queries and shifting relevance.
The local adapter imports the unchanged online core from the pinned checkout.
Its 21 matrix-completion/online tests passed (pytest, 16 September 2026).
The paper's description of stratified sampling differs from the release's
deterministic highest-score anchors; this study follows the pinned code.

Banking release notes for 1.0.1 were read, including corrected card cashback
and ATM-refund gold. This study constructs new numerical cases from selected
documents; no author task gold or source annotations enter treatment input.
Original document IDs, texts and hashes accompany every experimental run.
The source MIT and EARM Apache licenses are retained alongside this note.

Native route adapted from procedure-transfer/scripts/runtime.py at sibling
revision dcdc0d6f54dde235549f8abfba407598b6635667. Reuse is read-only model weights
and the documented tokenizer/MLX route, not learned adapters or data. Model
Qwen/Qwen3-4B-Instruct-2507 revision cdbee75f17c01a7cc42f958dc650907174af0554;
weight hashes verified before loading. The pinned MLX-LM version exposes real
trimmable KV caches; cache reuse/invalidation is measured rather than estimated.

Focused public search (16 September 2026) for experience-amortized retrieval
under revision returned EARM and derivative summaries, not a demonstrated
priority claim. Cached query-API metadata for MemoryData (2606.24775) and
StateMemBench (2608.19652) confirms substantial existing work on update costs
and evolving state. Our local conclusion must concern this learned access
component and competitive explicit controls, not novelty of memory updates.
The first multi-ID related-work API call was also rate-limited; spaced single-ID
requests succeeded. No API/OAI calls were parallelized.
