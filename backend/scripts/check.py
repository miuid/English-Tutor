#!/usr/bin/env python3
"""One-command check: run pytest + eval scorecard and report green/red.

Usage:
    python scripts/check.py           # pytest only (fast)
    python scripts/check.py --eval    # pytest + live eval (slow; needs API key)
    python scripts/check.py --help

Exit code: 0 if everything passes, 1 otherwise.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_pytest() -> bool:
    """Run pytest; return True if all pass."""
    print("=" * 60)
    print("Running pytest...")
    print("=" * 60)
    backend = Path(__file__).resolve().parent.parent
    env = os.environ.copy()
    # Windows temp-dir permission quirk — use project-local tmp
    env["TMP"] = str(backend / ".tmp")
    env["TEMP"] = str(backend / ".tmp")
    result = subprocess.run(
        [sys.executable, "-m", "pytest"],
        cwd=backend,
        env=env,
    )
    return result.returncode == 0


def run_eval() -> bool:
    """Run eval scorecard; return True if all pass."""
    print()
    print("=" * 60)
    print("Running eval scorecard (live LLM calls — this will take a few minutes)...")
    print("=" * 60)
    backend = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "app.eval"],
        cwd=backend,
    )
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run pytest + optional eval.")
    parser.add_argument("--eval", action="store_true", help="also run live eval (needs API key)")
    args = parser.parse_args()

    ok = run_pytest()

    if args.eval:
        ok = run_eval() and ok
    else:
        print()
        print("Tip: re-run with --eval to also validate all skills against the live model.")

    print()
    print("=" * 60)
    if ok:
        print("All checks passed.")
        return 0
    else:
        print("Some checks failed.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
