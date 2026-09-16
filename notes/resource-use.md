# Resource use

2026-09-16: execution begins on mac.lan, Mac13,2, 64 GiB unified memory.
Docker Model Runner's dedicated endpoint reports docker.io/ai/qwen3.8:27b-q4_K_M.
Initial process inspection found no Python training or experimental job.
Use serial model requests and check visible competing jobs before model work.
This is passive coordination, not a reservation; wall times are observations,
not isolated hardware benchmarks. Only this study's files are changed.
The initial workload uses NumPy EARM and the existing inference service;
no new model weights or gradient job is needed.
