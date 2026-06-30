.PHONY: all ch00 ch01 ch02 ch03 ch04 ch05 clean check-calc

PY := python3

all: ch01 ch02 ch03 ch04 ch05

check-calc:
	@command -v agent-calc >/dev/null 2>&1 || { echo "ERROR: agent-calc not on PATH"; exit 1; }
	@agent-calc --version

## ch00 — token-provider cost-per-quality ranking (data in data/)
ch00:
	@echo "See data/pricing.md + data/quality.md; ranking harness in models/00-ranking/"

## ch01 — optimal multi-provider routing LP + cost-of-privacy frontier
ch01: check-calc
	$(PY) models/01-routing-lp/route.py

## ch02 — self-host vs serverless break-even utilization
ch02: check-calc
	$(PY) models/02-selfhost/breakeven.py

## ch03 — the reasoning-token tax (cost per solved task)
ch03: check-calc
	$(PY) models/03-reasoning-tax/tax.py

## ch04 — the retry cascade (primary → fallback routing)
ch04: check-calc
	$(PY) models/04-retry-cascade/cascade.py

## ch05 — NPV of waiting (commit vs ride the price decline)
ch05: check-calc
	$(PY) models/05-npv-waiting/npv.py

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
