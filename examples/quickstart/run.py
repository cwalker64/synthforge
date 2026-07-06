"""Solve the bundled example suite and print a report.

Run with:  python examples/quickstart/run.py
"""

from synthforge.loop import LoopConfig, solve_task
from synthforge.report import render_text
from synthforge.synth.template import TemplateSynthesizer
from synthforge.tasks import load_example_suite


def main() -> None:
    suite = load_example_suite()
    synth = TemplateSynthesizer()
    config = LoopConfig(samples=1, repair_budget=3)

    solved = 0
    for task in suite:
        report = solve_task(task, synth, config=config)
        print(render_text(report))
        solved += int(report.solved)

    print(f"\nsolved {solved}/{len(suite)} tasks")


if __name__ == "__main__":
    main()
