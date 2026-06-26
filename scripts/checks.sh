#!/usr/bin/env bash
# Run the same checks as CI: lint, format, type-check, tests.
# Usage: bash scripts/checks.sh
set -euo pipefail

echo "==> ruff check"
ruff check .

echo "==> ruff format --check"
ruff format --check .

echo "==> mypy"
mypy

echo "==> pytest"
pytest --cov=synthforge --cov-report=term-missing

echo "All checks passed."
