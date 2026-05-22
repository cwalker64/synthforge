# synthforge

[![CI](https://github.com/cwalker64/synthforge/actions/workflows/ci.yml/badge.svg)](https://github.com/cwalker64/synthforge/actions/workflows/ci.yml)
[![CodeQL](https://github.com/cwalker64/synthforge/actions/workflows/codeql.yml/badge.svg)](https://github.com/cwalker64/synthforge/actions/workflows/codeql.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**A small, offline-first framework for program synthesis and test-based evaluation.**

synthforge turns a task prompt into candidate programs, runs them against unit
tests in an isolated subprocess, and repairs the failures — the classic
*generate → test → repair* loop, implemented in pure Python with **no runtime
dependencies and no network access**. The reference backends are deterministic,
so runs are reproducible on any machine.

```
   Task ─► Synthesizer ─► Candidates ─► Evaluator ─► pass/fail
                                             │
                                             ▼ (on failure)
                                          Repairer ─► retry
```

## Why

Most code-eval harnesses assume a hosted model and score a single generation.
synthforge separates the three concerns behind small protocols so you can swap
any stage — and ships pure-Python reference implementations so the whole thing
works offline, in CI, with the checkout you already have.

- **Synthesize** — the `template` backend maps a prompt onto a library of code
  templates; `fixture` replays recorded completions; `perturb` mutates a seed.
- **Evaluate** — candidates run in a sandboxed subprocess with a wall-clock
  timeout and a reliability guard; results roll up into `pass@k`.
- **Repair** — an AST-driven search proposes single-edit fixes for failing
  candidates and keeps whatever improves the pass rate.

## Install

```bash
pip install -e ".[dev]"
```

## Quickstart

```bash
# solve the bundled example suite, offline
synthforge run

# your own suite, as a Markdown table
synthforge run suite.jsonl --format markdown
```

```python
from synthforge import LoopConfig, Task, solve_task
from synthforge.synth.template import TemplateSynthesizer

task = Task(
    task_id="add",
    prompt="return the sum of a and b",
    entry_point="add",
    tests=("assert add(2, 3) == 5",),
    signature="def add(a, b):",
)
report = solve_task(task, TemplateSynthesizer(), config=LoopConfig(samples=1))
print(report.solved)  # True
```

## Documentation

- [docs/usage.md](docs/usage.md) — CLI and library usage, task format
- [docs/architecture.md](docs/architecture.md) — how the pieces fit together
- [docs/design-notes.md](docs/design-notes.md) — decisions and the threat model
- [docs/api-reference.md](docs/api-reference.md) — the public surface
- [examples/](examples/) — runnable examples

## A note on safety

The subprocess boundary and reliability guard stop a *misbehaving* candidate
from taking down the evaluator. They are **not** a security sandbox — run
genuinely untrusted code inside a container or VM. See the design notes.

## License

MIT — see [LICENSE](LICENSE).
