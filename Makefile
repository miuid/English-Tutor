.PHONY: check check-all

check:
	cd backend && uv run python scripts/check.py

check-all:
	cd backend && uv run python scripts/check.py --eval
