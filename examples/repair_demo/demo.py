"""Watch the repair loop fix a deliberately buggy candidate.

The fixture synthesizer hands the loop a wrong implementation (uses ``-``
instead of ``+``). The rule repairer swaps the operator and the loop confirms
the fix against the tests.

Run with:  python examples/repair_demo/demo.py
"""

from synthforge.loop import LoopConfig, solve_task
from synthforge.report import render_text
from synthforge.synth.fixture import FixtureSynthesizer
from synthforge.types import Task


def main() -> None:
    task = Task(
        task_id="add",
        prompt="return the sum of a and b",
        entry_point="add",
        tests=("assert add(2, 3) == 5", "assert add(10, 5) == 15"),
    )
    buggy = "def add(a, b):\n    return a - b\n"
    synth = FixtureSynthesizer({"add": [buggy]})

    report = solve_task(task, synth, config=LoopConfig(samples=1, repair_budget=3))
    print(render_text(report))
    for step in report.repairs:
        print(f"  round {step.iteration}: {step.operator} -> improved={step.improved}")


if __name__ == "__main__":
    main()
