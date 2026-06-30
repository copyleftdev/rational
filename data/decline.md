# LLM price decline + reserved-commit discounts

**Observed: 2026-06-30** via live search/fetch. Used by Chapter 05 (NPV of waiting).

## Q1 — How fast do token prices fall?

The decline rate depends entirely on *what you hold fixed*:

| Regime | What it measures | Low | **Central** | High | Sources |
|---|---|--:|--:|--:|---|
| **Fixed-quality** | same capability getting cheaper (migrate to equal-quality alts) | 50%/yr (~2×) | **80%/yr (~5×)** | 90%/yr (~10×) | a16z LLMflation; Epoch AI |
| **Frontier** | always running the best model | 0%/yr (flat) | **30%/yr (~1.4×)** | 50%/yr (~2×) | a16z; BenchLM 2026 |

- a16z "LLMflation": fixed-quality (GPT-3-class) fell **~10×/yr**, ~1000× over 3 yrs ($60→$0.06/M). GPT-4-equivalent ~62× since Mar 2023.
- Epoch AI: price to hit a fixed benchmark fell **~50×/yr** (2020–early 2025); GPT-4-level on GPQA ~40×/yr. Post-2024 tails of 200–900×/yr are flagged **low-confidence by Epoch itself** — excluded from the forward model.
- Frontier is sticky and strategy-driven: top flagship fell ~6× over 3 yrs (~45%/yr) **but OpenAI raised** GPT-5→5.5 ($1.25/$10 → $5/$30) while Anthropic cut Opus ~3×. "Newer flagship ≠ higher price; direction depends on provider." → central ~30%/yr, episodes of increase.
- Single-model step-cuts are lumpy (~40–80% per cut event); the smooth curve is realized only by migrating to equal-quality alternatives.

## Q2 — Reserved / committed-capacity discounts (vs on-demand)

| Offering | Term | Discount | Conf |
|---|---|--:|---|
| AWS Savings Plans (P5/H100) | 1 yr / 3 yr | ~25% / **~45%** | High |
| CoreWeave reserved | 1 yr / 3 yr | ~35% / ~55% | Med |
| Lambda reserved (H100) | 1 yr / 3 yr | ~20% / ~26% | Med |
| RunPod / general GPU | 1–3 yr | ~45–60% | Med |
| Azure OpenAI/Foundry PTU reservation | monthly / 1 yr | up to ~64% / ~70% **vs hourly PTU** (≈30–50% vs token pay-go after right-sizing) | High |
| AWS Bedrock Provisioned Throughput | 1 mo / 6 mo | ~10% / ~28% | Med |
| OpenAI / Anthropic enterprise token commits | annual | negotiated, opaque (~15–30% at >$500K/yr) | **Low — not public** |

**Representative plug-in:** ~30% (1-yr) to ~45% (3-yr) reserved discount.

## Q3 — Owned-GPU depreciation (for the self-host angle, cross-ref Ch02)
H100 resale: peak ~$40–50k (mid-2024) → used $15–28k (2026). Holds ~75–85% for 24 mo, then accelerates to **~10–20%/yr** as Blackwell floods supply. **Model: ~20%/yr depreciation, 3–4 yr economic life, ~35% residual at year 3.** (Physical life 5–9 yr, but economic relevance collapses sooner.)

## Plug-in recommendation
Fixed-quality decline: **central 80%/yr**. Frontier: **central 30%/yr**. Reserved discount: **~30% (1yr) / ~45% (3yr)**.

**Flags:** Epoch 200–900×/yr tails (non-persistent); all OpenAI/Anthropic enterprise discounts (non-public); H100 used-price levels vary by source; Azure "64–70%" is vs hourly PTU, not token pay-go.
