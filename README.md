# deal-check — Exact financial models for AI infrastructure decisions

> Stop guessing your AI infra costs. Make the LLM do the modeling — but **never** the arithmetic.

This repo is the companion to the guide *"The AI Cost Modeling Handbook."* Every number here is produced by a two-stage pipeline:

1. **Research agents** pull *live, cited* provider prices and quality benchmarks (observed dates recorded in `data/`).
2. **[`agent-calc`](https://github.com/?)** — an AI-native **exact rational** computation kernel — does the arithmetic. No float drift, no LLM hallucinating a multiplication. Where a solver must use floats (LP), the result is **re-verified in exact rationals**.

The point: a cost model you can *audit*. Re-run any chapter and you get bit-identical numbers, with the source of every input price one file away.

## The workload model

All chapters share one production-agentic workload profile (Hermes-Agent-style tool loops):

| Component | Share of tokens | Why |
|---|---|---|
| Fresh input | 21.25% | New context each turn |
| Cached input | 63.75% | System prompt + skills + history re-sent every tool-loop step (75% of input is a cache hit) |
| Output | 15% | Agents emit little text, mostly tool-call args |

`blended $/1M = 0.2125·in + 0.6375·cached + 0.15·out`

## Chapters

| # | Model | Money question | agent-calc domain | Status |
|---|---|---|---|---|
| 00 | Token-provider ranking | Cheapest provider per *quality unit* to drive an agent | `rational` | ✅ `data/` |
| 01 | [Multi-provider routing LP](models/01-routing-lp/) | Optimal traffic split minimizing spend under a quality + privacy floor | `linear` + `eval` | ✅ |
| 02 | [Self-host vs. serverless](models/02-selfhost/) | Utilization a GPU node must hold to beat per-token API | `finance`, `eval` | ✅ |
| 03 | [The reasoning-token tax](models/03-reasoning-tax/) | Cost per *solved task* once you count thinking tokens | `eval`, `solve` | ✅ |
| 04 | [The retry cascade](models/04-retry-cascade/) | Cheap→premium escalation: near-total coverage at a fraction of frontier cost | `stats`, `eval` | ✅ |
| 05 | NPV of waiting | Reserved-capacity prepay vs. riding the price decline | `finance` | ⬜ |
| 06 | Prompt-cache ROI | Reuse count where caching pays off vs. write premium | `optimize`, `interval` | ⬜ |
| 07 | Agent-loop compounding | Why turn N costs O(N²) without compaction | `polynomial` | ⬜ |

## Reproduce

```bash
make ch01      # optimal routing LP frontier
make all       # every chapter
```

Every model script is self-contained Python that shells out to `agent-calc`. Inputs live in `data/` with observation dates and source URLs.
