# Frontier "premium fallback" models

**Observed: 2026-06-30** via live search/fetch. Used by Chapter 04 (retry cascade) as the reliable premium tier for the hard task tail. Closed-weight — outside the repo's open-weights default, included only as the cascade's escalation target (the user's "no hard constraints" path).

| model | input $/M | cached $/M | output $/M | SWE-V | agentic-success (0–100)¹ | caching | batch 50% | source |
|---|---:|---:|---:|---:|---:|---|---|---|
| **Claude Opus 4.8** | 5.00 | 0.50 | 25.00 | 88.6% | **88** | ✅ | ✅ | morphllm.com/claude-benchmarks; Claude API ref |
| Claude Sonnet 4.6 | 3.00 | 0.30 | 15.00 | 79.6% | 82 | ✅ | ✅ | morphllm.com/claude-benchmarks |
| Claude Fable 5 ⚠️ | 10.00 | 1.00 | 50.00 | 95.0% | 92 | ✅ | ✅ | llm-stats.com/blog/research/claude-fable-5-review |
| OpenAI GPT-5.5 | 5.00 | 0.50 | 30.00 | 82.6% | 84 | ✅ | ✅ | openai.com/index/introducing-gpt-5-5 |
| OpenAI GPT-5.1 | 1.25 | 0.125 | 10.00 | ~73–76 | 79 | ✅ | ✅ | pricepertoken.com/.../openai-gpt-5.1 |
| **Gemini 3.1 Pro** | 2.00 | 0.20 | 12.00 | 80.6% | **81** | ✅ | ✅ | artificialanalysis.ai/models/gemini-3-1-pro-preview |

¹ Normalized to the Ch00 open-weights anchors (DeepSeek V3.2=77, MiniMax M2=73, GLM-4.6=71, Kimi K2=66). SWE-V solidly sourced; τ²/BFCL components largely **estimated** → treat normalized scores as ±3–5.

## Chosen tiers for the cascade
- **Top reliable fallback: Claude Opus 4.8** — $5/$0.50/$25, success 88. (Fable 5 scores higher at 92 but was temporarily unavailable as of 2026-06-12 under export-control directives, ~restore 2026-07-01 — so Opus 4.8 is the dependable top tier; Fable 5 is an optional above-Opus tier once GA.)
- **Mid escalation tier: Gemini 3.1 Pro** — $2/$0.20/$12, success 81. Cheapest frontier-class; good first escalation before Opus.

## Flags
τ²-bench / BFCL exact per-model numbers are inconsistently published mid-2026; agentic-success is anchored to SWE-V + vendor claims. OpenAI/Google pricing from third-party trackers — re-verify on official pages before billing-critical use. Gemini/GPT reprice ~2× in / 1.5× out above 200K–272K-token prompts.
