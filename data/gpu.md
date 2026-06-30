# GPU cost + inference throughput

**Observed: 2026-06-30** via live search/fetch. Used by Chapter 02 (self-host vs serverless). Throughput assumptions dominate the result — bands, not points.

## Rental ($/GPU/hr) — cheapest *reliable fixed* rate card

| GPU | on-demand | 1-yr reserved | source |
|---|---:|---:|---|
| H200 141GB SXM | 3.50 (Hyperstack) | 2.45 (Hyperstack) | hyperstack.cloud/gpu-pricing |
| H100 80GB SXM | 2.40 (Hyperstack) | 1.89 (Lambda 1yr) | hyperstack.cloud; lambda.ai/pricing |
| B200 | 6.11 (DataCrunch/Verda) | 4.58 (Verda 2yr, computed) | verda.com/pricing |
| A100 80GB | 1.35 (Hyperstack) | 0.95 (Hyperstack) | computeprices.com |

Marketplace floors (Vast/SF Compute) run lower but volatile; spot ~40–65% below on-demand but interruptible. Premium clouds (AWS/CoreWeave) 1.5–2× higher. AWS Blackwell/H200 Capacity Block +~15% eff. 2026-07-01.

## Purchase (street, per card) + power

| Card | street price | TDP (W) |
|---|---:|---:|
| H200 141GB | ~31,000 (28–35k NVL/PCIe; trending down) | 700 |
| H100 80GB SXM | ~27,000–40,000 (system÷8) | 700 |
| B200 | ~40,000 | 1000 |

Source: intuitionlabs.ai/articles/nvidia-ai-gpu-pricing-guide (2026-04-14); jarvislabs.ai h200-price; NVIDIA TDP specs. No NVIDIA MSRP — medium confidence.

## Node sizing + served throughput (aggregate, high concurrency)

DeepSeek V3.2 (~671B MoE, ~37B active, **FP8-native**, sparse attention) → **8×H200** (or 8×H100) per node.

| Model | node | engine | aggregate tok/s | quant | concurrency | source | conf |
|---|---|---|---:|---|---|---|---|
| DeepSeek V3.2 | 8×H200 | SGLang 0.5.6 | ~9,000 (peak 27.7K) | FP8* | ≤1000 | docs.gpustack.ai/.../deepseek-v3.2/h200 | Med-high |
| DeepSeek V3.2 | 8×H200 | vLLM 0.13.0 | 5,714 | FP8* | ≤1000 | (same) | Med-high |
| DeepSeek V3 (proxy) | 8×H200 | vLLM Wide-EP | ~17,600 (2,200/GPU) | FP8 | large EP | vllm.ai/blog/2025-12-17 | High |
| DeepSeek V3/R1 (proxy) | GB200 NVL72 | SGLang PD+EP | decode 13,386/GPU | NVFP4 | batch 1408 | lmsys.org/blog/2025-09-25 | High (Blackwell) |

**Planning bands used in Ch02 (aggregate tok/s per 8-GPU node):**
- **H200 (Hopper):** 6,000 / 7,500 / 9,000 (low/mid/high)
- **B200 (Blackwell):** 24,000 / 30,000 / 38,000  (~4× Hopper decode; per-GPU 9–13K on GB200)

\* gpustack page labels BF16; conflicts with V3.2's FP8-native design — relative engine ranking (SGLang > vLLM) is the safe takeaway; absolute values medium confidence.

## API comparison price (from Ch01)
- DeepSeek V3.2 @ DeepInfra (US, ZDR): **$0.195125 /1M** blended — the apples-to-apples target.
- Floor: DeepSeek V4 Flash @ Fireworks: **$0.0896 /1M** — the API price keeps dropping.
