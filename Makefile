.PHONY: all ch00 ch01 clean check-calc

PY := python3

all: ch01

check-calc:
	@command -v agent-calc >/dev/null 2>&1 || { echo "ERROR: agent-calc not on PATH"; exit 1; }
	@agent-calc --version

## ch00 — token-provider cost-per-quality ranking (data in data/)
ch00:
	@echo "See data/pricing.md + data/quality.md; ranking harness in models/00-ranking/"

## ch01 — optimal multi-provider routing LP + cost-of-privacy frontier
ch01: check-calc
	$(PY) models/01-routing-lp/route.py

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
