# Chapter 06 — Prompt-cache ROI

**The money question:** prompt caching looks like free money, but a cache *write* often costs **more** than a normal input token (Anthropic charges 1.25× at 5-min TTL, 2× at 1-hr), while reads are cheap (0.1–0.5×). So caching is a bet: you pay a write premium up front to save on reads — and it only pays if you **reuse** the prefix enough times before it expires. How many reuses is "enough"?

For a prefix reused across N calls (write once, read N−1 times):
```
no-cache   = N · L · p_in
cache      = L · p_write + (N-1) · L · p_read
break-even   N* = (p_write - p_read) / (p_in - p_read)
savings(N)   = 1 - [p_write + (N-1)·p_read] / [N · p_in]
ceiling      = 1 - p_read/p_in        (N → ∞)
```

`agent-calc` computes N* and savings exactly (`eval`) and the cost **band** under uncertain reuse via the `interval` domain (`polynomial_range`).

## Results

| Provider | break-even N* | save@2 | save@5 | save@10 | ceiling |
|---|--:|--:|--:|--:|--:|
| DeepInfra V3.2 (0.5× read) | 1.00 | 25% | 40% | 45% | 50% |
| DeepSeek direct (0.1× read) | 1.00 | 45% | 72% | 81% | 90% |
| OpenAI GPT-5.1 (0.1× read) | 1.00 | 45% | 72% | 81% | 90% |
| Fireworks (0.5× read) | 1.00 | 25% | 40% | 45% | 50% |
| Anthropic Opus 5-min TTL (write 1.25×) | 1.28 | 32% | 67% | 78% | 90% |
| Anthropic Opus 1-hr TTL (write 2×) | 2.11 | −5% | 52% | 71% | 90% |

`N*` = total calls sharing the prefix before caching pays.

### Reuse uncertain — the cost band (`interval`)

A Hermes agent task makes N tool-loop calls reusing an 8,000-token prefix; N ∈ [3, 20]. On the **strictest** tier (Anthropic 1-hr write=2×):

| | cost per task (3 … 20 reuses) |
|---|---|
| cache | **$0.088 … $0.156** |
| no-cache | $0.120 … $0.800 |

At 20 reuses, caching cuts the prefix bill **80%** — even with the 2× write premium.

## What this chapter proves

1. **Caching pays almost immediately.** Any provider with no write fee (DeepInfra, DeepSeek, OpenAI, Fireworks) breaks even at **N\*=1** — the second call already wins. Even the harshest write premium on the market (Anthropic 1-hr, 2×) breaks even at just **3 calls**. There is essentially no realistic agent workload where caching a reused prefix is the wrong call.

2. **The write premium only matters at tiny reuse.** Anthropic 1-hr is −5% at N=2 (premium not yet amortized) but +52% by N=5 and +71% by N=10. If you reuse a prefix only once or twice, pick the cheap-write TTL (5-min) or skip caching; if you reuse it 5+ times, even the 2× write is irrelevant.

3. **Read multiplier sets the ceiling, not the write fee.** Long-run savings = `1 − p_read/p_in`: providers with 0.1× reads cap at **90%**, 0.5× reads at **50%**. When choosing a provider for a cache-heavy agent, the *read* multiplier is the number that compounds.

4. **This is why the guide assumes 75% cache-hit.** Every chapter's blended workload bills 63.75% of tokens at the cached rate. This chapter is the justification: agent tool-loops reuse a large prefix 10–20× per task, landing deep in the high-savings regime where caching is a 50–90% discount on input, not a rounding error. (See Ch07 for *why* the reused prefix is so large — it grows quadratically.)

**Practical rule for Hermes Agent:** cache the system prompt + tool definitions + loaded skills (the stable prefix) on every provider that supports it. Prefer 0.1×-read providers for cache-heavy loops. Only worry about TTL/write tiers if your reuse count per cache lifetime is < 3.

## Caveats
Assumes a single reused prefix and N reads within one TTL window; real caches can evict early or refresh (re-charging the write). Provider read/write multipliers from `data/pricing.md` + `data/frontier.md`. The break-even is exact; the savings ceiling assumes steady reuse.

## Reproduce
```bash
make ch06
# or: python3 models/06-cache-roi/cache.py
```
