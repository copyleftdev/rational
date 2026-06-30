# Provider pricing — open-weights token providers

**Observed: 2026-06-30.** USD per 1M tokens. Filters for this project: open-weights model, prompt caching supported, no-train. `cached` = cached-input read price.

> ⚠️ Catalog churn: several named models (DeepSeek V3.2, GLM-4.6, Kimi K2, MiniMax M2) are now *legacy* on big serverless providers; current flagships are DeepSeek V4 Flash/Pro, GLM-5.2, Kimi K2.6/K2.7, MiniMax M3. Pricing for both generations recorded below. A few decimals were read via fetch summarizers — confirm exact cents before billing-critical use.

## Used in the models (Tier-1, proven quality)

| key | model @ provider | input | cached | output | caching | batch | no-train | jurisdiction | source |
|---|---|---:|---:|---:|---|---|---|---|---|
| A | DeepSeek V3.2 @ OpenRouter | 0.23 | 0.023 | 0.34 | auto (DeepSeek 0.1×) | none | opt-out + ZDR filter | CN upstream | openrouter.ai/deepseek/deepseek-v3.2 |
| B | DeepSeek V3.2 @ DeepInfra | 0.26 | 0.13 | 0.38 | yes | 20% | yes, ~0 retention | **US** | deepinfra.com/pricing |
| C | MiniMax M2 @ MiniMax | 0.30 | 0.03 | 1.20 | yes | none | yes; ZDR enterprise-only | CN | platform.minimax.io/docs/guides/pricing-paygo |
| E | GLM-4.6 @ z.ai | 0.60 | 0.11 | 2.20 | yes | none | yes; ZDR cloud mode | CN | docs.z.ai/guides/overview/pricing |
| F | Kimi K2 @ DeepInfra | 0.50 | 0.40 | 2.00 | yes | 20% | yes, ~0 retention | **US** | deepinfra.com/pricing |
| H | DeepSeek R1 @ DeepInfra | 0.50 | 0.35 | 2.15 | yes | 20% | yes, ~0 retention | **US** | deepinfra.com/pricing |

## Emerging successors (cheaper; agentic quality not yet published — verify before use)

| model @ provider | input | cached | output | caching | batch | no-train | jurisdiction | source |
|---|---:|---:|---:|---|---|---|---|---|
| DeepSeek V4 Flash @ Fireworks | 0.14 | 0.028 | 0.28 | yes | 50% | ZDR default (open models) | **US** | fireworks.ai/pricing |
| MiniMax M3 @ Fireworks | 0.30 | 0.06 | 1.20 | yes | 50% | ZDR default | **US** | fireworks.ai/pricing |
| DeepSeek V4 Pro @ Fireworks | 1.74 | 0.145 | 3.48 | yes | 50% | ZDR default | **US** | fireworks.ai/pricing |

## Excluded by filters
- **Qwen3-235B @ DeepInfra** ($0.09/$0.10, near-free) — **no prompt caching** → fails hard caching filter.
- **Nous Portal (native Hermes 4)** ($0.05/$0.20) — no caching on Hermes models + weakest privacy (collects anonymized conversation text, no no-train/ZDR).
- **NVIDIA NIM** — no per-token retail; free tier trains on data. **Lambda** — inference API winding down.

Full cross-provider sweep (Together, Fireworks, Novita, Groq, Cerebras, etc.) captured in research notes; the rows above are the constraint-satisfying subset.
