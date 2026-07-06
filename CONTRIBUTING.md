# Contributing

Thanks for taking the time to contribute! This is a small project and the bar
is simple: keep it correct, offline, and dependency-free.

## Development setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install   # optional but recommended
```

## Before you open a PR

Run the same checks CI runs:

```bash
ruff check .
ruff format --check .
mypy
pytest --cov=synthforge
```

Or use the helper: `bash scripts/checks.sh`.

## Guidelines

- **Stay dependency-free at runtime.** The core must not grow third-party
  runtime dependencies. Dev/test tooling is fine.
- **Tests travel with code.** New behaviour needs a test in the same PR, next
  to the module it covers.
- **Keep commits small.** One logical change per commit; a readable history is
  worth more than a tidy squash.
- **Type everything.** `mypy` runs in strict mode over `synthforge/`.
- **New synthesizers/repairers** should implement the relevant protocol and, if
  generally useful, register themselves in the registry.

## Reporting bugs

Open an issue with a minimal reproduction. If it involves a task, include the
task JSON and the candidate source.
