# Agentic quality scores — open-weights models

**Observed: 2026-06-30.** Normalized 0–100 "agentic quality" = simple mean of available {BFCL v3, τ/τ²-bench overall, SWE-bench Verified} — all already on a ~0–100 scale, all tool-use relevant. Used as the divisor for cost-per-quality and as the quality coefficient in the routing LP.

> Artificial Analysis Intelligence Index v4.1 is shown for sanity only and **excluded** from the divisor — its compressed rescale is not comparable across this cohort.

| Model | BFCL v3 | τ/τ²-bench | SWE-V | **Agentic quality** | Confidence |
|---|---:|---:|---:|---:|---|
| DeepSeek V3.2 | — | τ² 80.4 | 73.1 | **77** | High |
| MiniMax M2 | — | τ² 77.2 | 69.4 | **73** | High |
| GLM-4.6 | 77.8* (4.5 proxy) | — | 68.0 | **~71** | Medium |
| Kimi K2 | — | τ² 66.1 | 65.8 | **66** | High |
| Qwen3 235B (2507) | 70.8 | τ²-tel 33† | 61.7 | **66** | Medium |
| DeepSeek R1 (0528) | — | τ¹ 58.7 | 49.2 | **54** | Medium |
| Llama 4 Maverick | — | ~68.5* | — | ~50 | Low |
| DeepSeek V3 | — | — | ~42* | ~40 | Low (stale) |
| Llama 3.3 70B | 77.3 (v2) | — | low | ~40 | Low (stale) |
| Hermes 4 405B | — | — | — | ~25 | Very low (no agentic data) |
| Hermes 4 70B | — | — | — | ~20 | Very low (no agentic data) |

\* proxy/unverified · † single harsh sub-domain, excluded as outlier

**Key caveat:** the Hermes *models* have **no published BFCL/τ²/SWE-V scores**. This project pairs a provider with Hermes the *agent framework*, so the driver model is chosen from the scored open-weights set above — Hermes-the-model is not a candidate.

**Sources (2026-06-30):** artificialanalysis.ai/models · gorilla.cs.berkeley.edu/leaderboard.html (BFCL) · arXiv 2512.02556 (DeepSeek V3.2) · arXiv 2507.20534 (Kimi K2) · github.com/MiniMax-AI/MiniMax-M2 · docs.z.ai (GLM-4.6) · huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507 · llm-stats.com/benchmarks/swe-bench-verified
