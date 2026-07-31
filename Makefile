.PHONY: check check-all

check:
	cd backend && python scripts/check.py

check-all:
	cd backend && python scripts/check.py --eval
