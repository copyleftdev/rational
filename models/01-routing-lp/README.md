# Chapter 01 — Optimal multi-provider routing (a linear program)

**The money question:** you don't have to send all your traffic to one provider. Given a menu of open-weights pairings with different prices, quality, and *jurisdiction*, what split **minimizes spend** while staying above a quality bar — and what does **privacy actually cost** you?

This is a textbook **linear program**, and `agent-calc` solves it directly (`solve_lp`) — then we re-verify the winning allocation's cost in **exact rationals** so no float drift sneaks into the headline number.

## The menu (proven Tier-1 pairings)

Blended $/1M under the [shared workload model](../../README.md#the-workload-model). Quality = normalized agentic score (BFCL / τ²-bench / SWE-V). Jurisdiction matters for the privacy constraint.

| | Pairing | Blended $/1M | Quality | Jurisdiction |
|---|---|---:|---:|---|
| A | DeepSeek V3.2 @ OpenRouter | 0.1145 | 77 | CN upstream (ZDR filter) |
| B | DeepSeek V3.2 @ DeepInfra | 0.1951 | 77 | **US** (ZDR default, SOC2) |
| C | MiniMax M2 @ MiniMax | 0.2629 | 73 | CN |
| E | GLM-4.6 @ z.ai | 0.5276 | 71 | CN |
| F | Kimi K2 @ DeepInfra | 0.6613 | 66 | **US** |
| H | DeepSeek R1 @ DeepInfra | 0.6519 | 54 | **US** |

## The program

Decision variables `x_i` = fraction of total token traffic to pairing *i*.

```
minimize    Σ blended_i · x_i                      (total $/1M)
subject to  Σ x_i           = 1                     (allocate all traffic)
            Σ quality_i·x_i ≥ 74                    (quality floor)
            Σ US_i·x_i      ≥ θ                     (privacy knob — swept)
            0 ≤ x_i ≤ 0.60                          (per-endpoint cap: rate limits / no SPOF)
```

The 0.60 cap is the realism that makes this non-trivial: no single endpoint absorbs your whole load (rate limits), and you don't want a single point of failure.

## The cost-of-privacy frontier

Sweeping the US-jurisdiction floor **θ** from 0 → 100%:

| US floor θ | min $/1M | $/mo @ 1B | avg quality | optimal allocation |
|---:|---:|---:|---:|---|
| 0.00 – 0.40 | 0.1468 | **$146.77** | 77.0 | A=0.60, B=0.40 |
| 0.50 | 0.1548 | $154.83 | 77.0 | A=0.50, B=0.50 |
| 0.60 | 0.1629 | $162.89 | 77.0 | A=0.40, B=0.60 |
| 0.70 | 0.2166 | $216.62 | 74.7 | A=0.30, B=0.60, H=0.10 |
| 0.80 | 0.2716 | $271.61 | 74.0 | A=0.20, B=0.60, F=0.13, H=0.07 |
| 0.87 | 0.3105 | $310.48 | 74.0 | A=0.13, B=0.60, F=0.27 |
| **0.872** | 0.3116 | **$311.59** | 74.0 | A=0.13, B=0.60, F=0.27 |
| ≥ 0.873 | — | **INFEASIBLE** | — | the privacy wall |

## Three things this LP tells you that intuition doesn't

1. **The first 40% of US-jurisdiction traffic is free.** The cost-optimal blend *already* routes 40% to a US endpoint — because the cheapest pairing (A) is capped at 60%, the overflow naturally lands on US DeepInfra (B). Demanding "≥40% US" changes nothing.

2. **The marginal cost of privacy is convex.** Going 40→60% US is cheap (~$8/mo per 10 points). Past 60% the quality floor starts binding, forcing low-quality fillers (Kimi, R1) into the mix, and the curve steepens hard: 60→87% nearly **doubles** your bill.

3. **There's a hard wall at 87.2% US.** You *cannot* run more US-jurisdiction traffic at quality ≥ 74 with today's menu — there is exactly **one** high-quality US endpoint (DeepSeek V3.2 @ DeepInfra, q77, capped at 60%). Beyond the wall, math forces average quality below the floor. To break it you must either (a) onboard a *second* high-quality US-jurisdiction provider, (b) raise DeepInfra's cap and accept single-point-of-failure risk, or (c) lower the quality bar.

## Why two engines

`agent-calc`'s LP solver is f64 (`good_lp`/microlp) — it reports `"exactness": "approximate_f64"`. So we don't trust its objective for the headline. We take the optimal **allocation**, snap it to exact rationals, and recompute the cost with `agent-calc eval` (exact rational). The frontier's `$/1M` column is the *exact* re-verified cost, not the solver's float.

## Reproduce

```bash
make ch01
# or:
python3 models/01-routing-lp/route.py
```

Prices: [`data/pricing.md`](../../data/pricing.md). Quality: [`data/quality.md`](../../data/quality.md). Both carry observation dates + source URLs.
