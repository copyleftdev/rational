# Chapter 07 — Agent-loop compounding (the O(K²) tax)

**The money question:** a multi-turn agent re-sends its growing context every step — at step *k* the input is the base prompt plus *every prior tool call and result*. Per-step input grows linearly, so the **cumulative** token bill over a K-step task grows **quadratically**. How bad is it, and what tames it?

```
step-k input      = B + (k-1)·δ                          (linear per step)
cumulative over K = Σ (B+(k-1)δ) = (δ/2)·K² + (B-δ/2)·K   (quadratic — a polynomial in K)
```

`agent-calc` evaluates that cumulative-token **polynomial** exactly (`polynomial/evaluate`) at each K, and `eval` turns it into dollars per regime.

## The three regimes

- **Naive** — pay full input price on the quadratic.
- **Cached** — the re-sent prefix bills at the cache-read rate (Ch06), scaling the quadratic's slope by `read/in`.
- **Compacted** — cap retained history at a window W (summarize/truncate); per-step input flattens, so cumulative goes **linear**.

## Results

Base context B = 8,000 tok, +δ = 1,500 tok/step, compaction window W = 20,000, price $0.26/$0.13 per M (in/read).

**Per-step input grows linearly:** step 1 = 8,000 · step 10 = 21,500 (2.7×) · **step 50 = 81,500 (10.2×)**. Your 50th tool call's input costs 10× your first.

| K steps | cum tokens (naive) | naive $ | cached $ | compact $ | naive/compact |
|--:|--:|--:|--:|--:|--:|
| 5 | 55,000 | 0.0143 | 0.0090 | 0.0143 | 1.0× |
| 10 | 147,500 | 0.0384 | 0.0220 | 0.0384 | 1.0× |
| 20 | 445,000 | 0.1157 | 0.0626 | 0.1083 | 1.1× |
| 50 | 2,237,500 | 0.5817 | 0.3015 | 0.3267 | 1.8× |
| 100 | 8,225,000 | 2.1385 | 1.0896 | 0.6907 | **3.1×** |

**The quadratic is real:** 100-step cumulative = 8,225,000 tokens vs 147,500 at 10 steps — **55.8× the tokens for 10× the steps**.

## What this chapter proves

1. **Long agent tasks are quadratic, not linear.** Doubling task length nearly quadruples the token bill. A 100-step task isn't 10× a 10-step task — it's **56×**. This is the hidden cost of "let the agent keep going."

2. **Caching bends the curve; compaction breaks it.** Caching scales the slope (here 0.5× read → roughly half the naive cost at every K) but the growth is *still quadratic* — at 100 steps cached is $1.09, better but climbing. Compaction caps per-step input, turning the curve **linear**: at 100 steps it's $0.69 (3.1× under naive) and the gap widens without bound as K grows. For genuinely long loops, **compaction is the only thing that stops quadratic blow-up; caching just lowers the constant.**

3. **They compose.** Cached *and* compacted is multiplicative — read-rate pricing on a linear token count. The cheapest long-running agent caps its window *and* caches the stable prefix. (The table shows each mitigation alone; combining them is the floor.)

4. **This closes the loop on the whole guide.** The quadratic re-send is exactly why the production-agentic workload (assumed in every chapter) is so input-heavy and so cache-dependent: the reused prefix from Ch06 is large *because* it compounds here. Ch06 (cache) and Ch07 (compaction) are the two levers that make the assumed 75% cache-hit / input-heavy profile not just realistic but necessary for cost control.

**Practical rule for Hermes Agent:** for any loop expected to exceed ~20 steps, enable history compaction (a context window cap with summarization) *and* prefix caching. Below ~10 steps the quadratic hasn't bitten yet and caching alone suffices.

## Caveats
Linear per-step growth (constant δ) is a simplification — real tool results vary in size; treat δ as the average. The compact column prices capped tokens at full input rate (compaction-only); combining with caching is lower still. The polynomial/quadratic structure is exact.

## Reproduce
```bash
make ch07
# or: python3 models/07-loop-compounding/loop.py
```
