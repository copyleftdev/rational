# Chapter 04 — The retry cascade

**The money question:** you don't have to pick one model for every task. Run a **cheap** model on everything, and **escalate** to a reliable premium model only on the residual failures. The cheap model clears the easy majority; you pay the premium price only on the hard tail. How much does that actually save — and when does it break?

**The model** (cheap → premium):
```
P(escalate) = 1 - p_cheap
P(solve)    = p_cheap + (1 - p_cheap)·q      # q = P(premium solves | cheap failed)
E[cost]     = C_cheap + (1 - p_cheap)·C_prem
cost/solved = E[cost] / P(solve)
```

`agent-calc` does the escalation probability via `stats/binomial_pmf` and the exact expected cost via `eval`.

## Tiers (from Ch00 + [`data/frontier.md`](../../data/frontier.md))

| Tier | Model | $/attempt | success p |
|---|---|--:|--:|
| cheap (open) | DeepSeek V3.2 | 2.44m | 0.77 |
| mid (frontier) | Gemini 3.1 Pro | 34.00m | 0.81 |
| top (reliable) | Claude Opus 4.8 | 73.00m | 0.88 |

(`m` = milli-dollars = $0.001 per task; task = 8,000 in / 600 visible out, 75% input cache-hit.)

## Results

| Strategy | cost/solved | coverage | % traffic → premium |
|---|--:|--:|--:|
| Cheap-only (single shot) | 3.17m | 77.0% | 0% |
| Premium-only Opus (single shot) | 82.96m | 88.0% | 100% |
| **Cascade V3.2 → Opus** | **19.78m** | **97.2%** | 23% |
| **Cascade V3.2 → Gemini → Opus** | **13.52m** | **99.5%** | 4.4% (23% hit Gemini) |

### Failure-correlation sensitivity (V3.2 → Opus)

`q` = chance the premium solves a task the cheap model *already failed*. Independence is `q = p_prem`; correlation drives it down.

| q | cost/solved | coverage | vs premium-only |
|--:|--:|--:|--:|
| 0.88 (independence) | 19.78m | 97.2% | 4.2× cheaper |
| 0.70 | 20.66m | 93.1% | 4.0× cheaper |
| 0.50 | 21.73m | 88.5% | 3.8× cheaper |
| 0.30 | 22.92m | 83.9% | 3.6× cheaper |

## What this chapter proves

1. **The cascade beats premium-only on *both* axes.** V3.2 → Opus solves **97.2%** of tasks (vs Opus-alone's 88%) at **¼ the cost-per-solved** ($19.78m vs $82.96m) — because only **23%** of tasks ever reach the expensive model. Higher coverage *and* 4× cheaper.

2. **Adding a mid-tier is almost free coverage.** Inserting Gemini 3.1 Pro between cheap and top pushes coverage to **99.5%** while *cutting* cost-per-solved to **$13.52m** — because the cheap+mid tiers absorb **95.6%** of all traffic, so the $73m Opus call fires on just 4.4% of tasks. Cascades are the cheapest way to buy near-total coverage.

3. **Retrying the same model is the trap.** Cost-per-solved for retry-until-success is always `C/p` — *unchanged* no matter how many times you retry. And for **deterministic** failures (the same task fails the same model every time), retrying doesn't even raise coverage. Only escalating to a **different, stronger** model moves both numbers. "Just add retries" is a no-op; "add a tier" is the win.

4. **The cost win is robust to correlation; the coverage win isn't.** Even when failures are strongly correlated (q=0.30 — the premium rarely rescues what the cheap model botched), the cascade is still **3.6× cheaper** than premium-only. But its *coverage* edge erodes (97% → 84%): if your hard tasks are hard for *everyone*, the cascade saves money but won't magically lift your solve rate. Measure `q` on your own workload.

**Practical rule for Hermes Agent:** default every task to a cheap efficient model (DeepSeek V3.2); auto-escalate on detected failure (tool error, low-confidence, self-check fail) to a mid frontier tier, and only then to a top reliable model. Three tiers gets you ~99.5% coverage at ~6× lower cost than sending everything to the frontier.

## Caveats
Per-attempt costs use the Ch03 task shape and assumed reasoning multipliers; success rates are the Ch00 agentic scores used as per-task `p` proxies. Frontier figures are closed-weight and partly estimated (see [`data/frontier.md`](../../data/frontier.md)). The *direction* (cascade ≫ single-model) is robust; localize the magnitude by measuring your own `p` per tier and the correlation `q`.

## Reproduce
```bash
make ch04
# or: python3 models/04-retry-cascade/cascade.py
```
