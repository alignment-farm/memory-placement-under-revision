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
