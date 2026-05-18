# Usage

## Install

```bash
pip install -e ".[dev]"   # from a checkout
```

synthforge has no runtime dependencies; the `dev` extra only pulls in the test
and lint tooling.

## Command line

Run the bundled example suite with the offline template synthesizer:

```bash
synthforge run
```

Point it at your own JSONL suite and choose a synthesizer and output format:

```bash
synthforge run path/to/suite.jsonl --synthesizer template --format markdown
```

`run` exits non-zero if any task is left unsolved, so it doubles as a gate in
CI. List the available synthesizers with:

```bash
synthforge synths
```

## Task format

A suite is a JSON Lines file with one task object per line:

```json
{"task_id": "add", "prompt": "Return the sum of a and b.", "entry_point": "add",
 "signature": "def add(a, b):", "tests": ["assert add(2, 3) == 5"]}
```

Required fields are `task_id`, `prompt`, `entry_point` and a non-empty `tests`
list. `signature`, `setup`, `reference`, `hints` and `timeout` are optional.

## Library

```python
from synthforge import LoopConfig, Task, solve_task
from synthforge.synth.template import TemplateSynthesizer

task = Task(
    task_id="add",
    prompt="return the sum of a and b",
    entry_point="add",
    tests=("assert add(2, 3) == 5", "assert add(-1, 1) == 0"),
    signature="def add(a, b):",
)

report = solve_task(task, TemplateSynthesizer(), config=LoopConfig(samples=1))
print(report.solved)          # True
print(report.best.pass_rate)  # 1.0
```

To evaluate a candidate you already have, skip synthesis:

```python
from synthforge import Candidate, evaluate

result = evaluate(task, Candidate("def add(a, b):\n    return a + b\n"))
```

See [api-reference.md](api-reference.md) for the full public surface.
