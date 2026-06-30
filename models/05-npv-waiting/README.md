# Chapter 05 — The NPV of waiting

**The money question:** a provider offers you a discounted *reserved* rate if you commit for a year (or three). Locking it in feels prudent. But token prices fall — fast. Is the committed discount actually a saving, or are you locking yourself *above* where pay-go will be in six months?

**The model.** You need a fixed monthly volume for T months. Two cash-flow streams:
```
COMMIT : flat monthly spend  S0·(1-disc)        for all T months
PAY-GO : month-t spend  S0·(1-g)^(t/12)         declining at annual rate g
```
NPV both at your cost of capital; lower-NPV-cost wins. Then find the **break-even decline rate g\***: above it, waiting wins; below it, committing wins.

`agent-calc` does the exact discounting (`finance/net_present_value`); monthly decline/discount factors are rationalized before the exact NPV.

## The decisive input: prices fall at *very* different rates

From [`data/decline.md`](../../data/decline.md):
- **Fixed-quality** (same capability getting cheaper — migrate to equal-quality alternatives): **~80%/yr** central (a16z/Epoch).
- **Frontier** (always run the best model — sticky, strategy-driven): **~30%/yr** central, with episodes of *increase* (OpenAI raised GPT-5→5.5).

## Results (S0 = $195/mo @ 1B tok, 12-mo horizon, 12% CoC, 30% commit discount)

| Workload / scenario | NPV cost | vs commit | winner |
|---|--:|--:|:--|
| **COMMIT** (flat 30% off) | 1556.91 | — | — |
| Fixed-quality, decline 50%/yr | 1661.84 | +6.7% | commit |
| **Fixed-quality, decline 80%/yr (central)** | **1198.50** | **−23.0%** | **pay-go** |
| Fixed-quality, decline 90%/yr | 974.49 | −37.4% | pay-go |
| Frontier, decline 0%/yr (flat) | 2224.16 | +42.9% | commit |
| **Frontier, decline 30%/yr (central)** | **1905.03** | **+22.4%** | **commit** |
| Frontier, decline 50%/yr | 1661.84 | +6.7% | commit |

### Break-even decline grid

g* = the annual decline at which pay-go ties commit (pay-go wins above):

| commit discount | 12-mo | 24-mo | 36-mo |
|--:|--:|--:|--:|
| 15% | 31.3% | 16.7% | 11.5% |
| 30% | 57.8% | 34.2% | 24.5% |
| 45% | 78.7% | 52.6% | 39.4% |

### Verdict at central decline rates — does committing *ever* win?

| Workload | Commit wins at |
|---|---|
| **Fixed-quality (80%/yr)** | **NEVER — pay-go always wins** (80% exceeds every g\* in the grid) |
| Frontier (30%/yr) | 15%/12mo, 30%/12mo, 30%/24mo, **45% at all terms** |

## What this chapter proves

1. **For commodity workloads, never lock in.** Fixed-quality prices fall ~80%/yr — faster than *any* reservable discount can offset (even a 45%/12-mo commit breaks even at 78.7%). Committing to reserved capacity for a commodity model means paying a flat rate while the spot market drops 80% underneath you. **Stay pay-go, stay flexible.**

2. **Only commit where prices are *sticky*.** Frontier capability declines slowly (~30%/yr) with occasional hikes, so a discounted commit genuinely wins — especially short terms. The asymmetry is the whole lesson: **reserve where the price won't move (frontier), ride the curve where it falls fast (commodity).**

3. **Longer terms are worse bets, and the grid shows why.** Every break-even g\* drops sharply with term: a 30% discount breaks even at 57.8%/yr over 12 months but only **24.5%/yr over 36 months**. Locking in 3 years requires prices to fall *slowly* for 3 years — a bet that loses badly in a market that's been falling 50–90%/yr. Short commits or none.

4. **Commit = utilization risk too (cross-ref Ch02).** Committed spend is flat regardless of usage; pay-go scales with it. If your volume might fall, the committed rate's *effective* cost rises — a second reason the flexible option is undervalued by gut instinct.

**Practical rule:** default to pay-go for open/commodity models. Consider a *short* (≤12-mo) reserved commit only for a frontier tier you'll keep saturated, and only if the discount clears the break-even for that term. Never sign a 3-year inference commitment in a market declining faster than ~25%/yr.

## Caveats
Decline rates are estimates (a16z/Epoch; Epoch's 200–900×/yr tails excluded as non-persistent). The monthly compounding factor is a rationalized approximation; the NPV discounting is exact. The verdict (commodity→wait, frontier→maybe-commit-short) is robust across the plausible decline range. Sources + flags in [`data/decline.md`](../../data/decline.md).

## Reproduce
```bash
make ch05
# or: python3 models/05-npv-waiting/npv.py
```
