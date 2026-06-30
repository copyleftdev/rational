# Chapter 02 — Self-host vs. serverless break-even

**The money question:** everyone's instinct is "at some volume, renting GPUs beats paying per token." When? We model self-hosting **DeepSeek V3.2** on your own node vs. buying the *same model* per-token from **DeepInfra** ($0.195/1M blended, US/ZDR — the apples-to-apples target from Ch01).

**The reframe intuition misses:** a self-hosted node costs the same at 5% load or 95% load; the API scales linearly with tokens. So the decision isn't a *dollar* volume — it's a **utilization**. Break-even utilization `u*` is the fraction of a node's 24/7 capacity you must keep busy to beat the API:

```
u* = node_$/mo × 1e6 / (capacity_tok_per_mo × API_$/1M)
```

If `u* > 100%`, self-hosting loses **even at full tilt** — one box can't be cheaper than the API no matter how hard you run it.

`agent-calc` does the arithmetic: `finance/amortize` for owned-hardware capex (cost-of-capital over 36-mo depreciation), `eval` (exact rationals) for `u*` and the break-even volume `V*`.

## Results

Node = 8 GPUs (DeepSeek V3.2 is a 671B FP8-native MoE → 8×H200 or 8×B200). Throughput = aggregate tok/s at high concurrency (see [`data/gpu.md`](../../data/gpu.md) for bands + sources). Cost of capital 8%, depreciation 36 mo, PUE 1.4, $0.12/kWh.

### Hopper — 8×H200 (capacity ≈ 19.7B tok/mo @ 100%)

| Procurement | $/node/mo | self-host $/1M @100% | break-even u* | break-even V*/mo |
|---|---:|---:|---:|---:|
| Rent on-demand | $20,440 | 1.0370 | **531% → NEVER** | 104.8B |
| Rent 1-yr reserved | $14,308 | 0.7259 | **372% → NEVER** | 73.3B |
| Own (amortized + power) | $8,458 | 0.4291 | **220% → NEVER** | 43.3B |

Across the throughput band (6k–9k tok/s) the owned case is **183%–275%** — still never. **On Hopper, self-hosting DeepSeek V3.2 cannot beat a $0.20/1M API in any procurement mode.**

### Blackwell — 8×B200 (capacity ≈ 78.8B tok/mo @ 100%)

| Procurement | $/node/mo | self-host $/1M @100% | break-even u* | break-even V*/mo |
|---|---:|---:|---:|---:|
| Rent on-demand | $35,682 | 0.4526 | **232% → NEVER** | 182.9B |
| Rent 1-yr reserved | $26,747 | 0.3393 | **174% → NEVER** | 137.1B |
| **Own (amortized + power)** | $11,009 | 0.1396 | **72% ✅** | 56.4B |

Across the throughput band (24k–38k tok/s) the owned case is **56%–89%**. This is the **only** configuration that beats the API.

## What this chapter actually proves

1. **"Self-host to save money" is a trap below hyperscale.** For a commodity open model priced at ~$0.20/1M, *renting* GPUs loses in **every** configuration tested — on-demand and reserved, Hopper and Blackwell. The serverless provider batches across thousands of tenants to hit a utilization you can't, and prices below your rental cost.

2. **Only owned Blackwell silicon, kept >72% busy 24/7, wins** — i.e. ~56 billion tokens/month of *steady, batched* load. Bursty traffic (a personal agent idle 18h/day) sits far under that line: you'd pay for a $11k/mo box to use a sliver of it.

3. **The API floor is moving against you.** Compared to the current floor (DeepSeek V4 Flash @ Fireworks, $0.0896/1M), **every** break-even utilization roughly *doubles* — even owned Blackwell needs ~100%+. Hardware depreciates over 36 months; per-token prices are dropping faster than that. You're amortizing a depreciating asset against a falling price.

**Corollary:** self-host for **privacy, control, customization, or latency** — not to cut the token bill. The cost case only closes at sustained hyperscale on owned next-gen hardware.

## Caveats (honest inputs)
Throughput is the dominant unknown and the bands are medium-confidence (the best public 8×H200 V3.2 dataset has an ambiguous precision label). The qualitative verdict is robust to wide throughput error because `u*` is so far from 100% on Hopper. Blackwell aggregate (24k–38k/node) is extrapolated from per-GPU GB200 decode figures. All sources + dates in [`data/gpu.md`](../../data/gpu.md).

## Reproduce
```bash
make ch02
# or: python3 models/02-selfhost/breakeven.py
```
