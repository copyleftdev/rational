# Chapter 03 — The reasoning-token tax

**The money question:** reasoning models emit hidden "thinking" tokens, billed at the **output** rate. A task whose visible answer is 600 tokens can bill 7,800. Does the higher success rate justify the burn — and what's the *right* unit to measure it in?

**The reframe:** not $/token, not $/attempt, but **cost per *solved* task**. If you retry until success, expected cost = cost-per-attempt ÷ success-rate:

```
cost_per_attempt = I_eff · price_in_blend + O · (1+k) · price_out
cost_per_solved  = cost_per_attempt / p
```

`k` = thinking tokens ÷ visible output. `p` = per-task success probability (proxied here from the Ch00 agentic quality score — flagged; sensitivity below).

`agent-calc` does the exact arithmetic (`eval`) and **solves** for the break-even success rate (`solve`, affine).

## Results

Task: 8,000 input / 600 visible output tokens, 75% input cache-hit. Costs in **milli-dollars** (`m` = $0.001) per task.

| Model | q | k | $/attempt | think-tax | $/solved | ×champion |
|---|--:|--:|--:|--:|--:|--:|
| **DeepSeek V3.2** | 77 | 4 | 2.44m | 37% | **3.17m** | **1.00×** |
| MiniMax M2 | 73 | 2 | 2.94m | 49% | 4.03m | 1.27× |
| Kimi K2 | 66 | 1 | 5.80m | 21% | 8.79m | 2.77× |
| GLM-4.6 | 71 | 5 | 9.78m | 67% | 13.77m | 4.35× |
| DeepSeek R1 | 54 | 12 | 19.87m | **78%** | 36.80m | **11.61×** |

"think-tax" = share of per-attempt cost that is *thinking* tokens.

### Break-even success rate to match the champion (exact, via `solve`)

| Model | needs p* | currently | |
|---|--:|--:|---|
| MiniMax M2 | 92.8% | 73% | reachable in principle |
| Kimi K2 | 183.0% | 66% | **impossible (>100%)** |
| GLM-4.6 | 308.6% | 71% | **impossible** |
| DeepSeek R1 | 627.0% | 54% | **impossible** |

### Reasoning-burn sweep (DeepSeek R1, p=54%)

| k (thinking tokens) | $/solved | ×champion |
|--:|--:|--:|
| 0 (0) | 8.13m | 2.6× |
| 4 (2,400) | 17.69m | 5.6× |
| 12 (7,200) | 36.80m | 11.6× |
| 20 (12,000) | 55.91m | 17.6× |

## What this chapter proves

1. **The efficient hybrid wins on both axes.** DeepSeek V3.2 has the *cheapest* output token ($0.38/M) **and** the *highest* success (77). So even a moderate 4× thinking burn (a 37% tax) is trivially absorbed. It's the champion.

2. **A heavy reasoner can be mathematically uncatchable.** DeepSeek R1 needs a **627% success rate** to match V3.2's cost-per-solved — i.e. *even a perfect 100%-success R1 is still far more expensive*, because its per-attempt token burn alone exceeds V3.2's entire cost-per-solved. The sweep confirms it: **even at k=0 (no thinking at all)**, R1 is 2.6× the champion. Expensive output tokens + lower agentic success doom it before reasoning is even considered.

3. **The reasoning tax only pays when output tokens are cheap.** Thinking is a multiplier on the output price. Pay $2.15/M and multiply by 12, and you've built the most expensive possible way to solve a task. Pay $0.38/M and the same multiplier barely registers. **Match heavy reasoning with cheap output pricing, or don't reason heavily.**

**Practical rule for Hermes Agent:** prefer an *efficient hybrid* (cheap output + strong tool-use) over a *reasoning-first* model for agentic loops. Reserve heavy reasoners for the rare task where the success lift is large *and* you've routed it to a cheap-output endpoint.

## Caveats
`k` (reasoning multiplier) and the quality→success mapping are assumptions, not measured per-task rates — that's why the chapter leads with **break-even** and **sensitivity** rather than a single number. The *ranking* is robust: it's driven by output price × burn, which are hard data. Measure your own task's `p` and `k` to localize the verdict.

## Reproduce
```bash
make ch03
# or: python3 models/03-reasoning-tax/tax.py
```
