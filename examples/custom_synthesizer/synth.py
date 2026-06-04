"""Plug in a custom synthesizer.

Any object with a ``name`` attribute and a ``synthesize(task, n)`` method
satisfies the Synthesizer protocol. Here we write one that always returns a
constant function, register it, and evaluate it.

Run with:  python examples/custom_synthesizer/synth.py
"""

from synthforge.eval.runner import evaluate
from synthforge.synth.registry import get_synthesizer, register
from synthforge.types import Candidate, Task


class ConstantSynthesizer:
    """Return ``entry_point`` implemented as ``return <value>``."""

    name = "constant"

    def __init__(self, value: int = 0) -> None:
        self._value = value

    def synthesize(self, task: Task, n: int = 1) -> list[Candidate]:
        source = f"def {task.entry_point}(*args, **kwargs):\n    return {self._value}\n"
        return [Candidate(source, origin=self.name)][:n]


def main() -> None:
    register("constant", ConstantSynthesizer)

    task = Task(
        task_id="always_42",
        prompt="always return 42",
        entry_point="answer",
        tests=("assert answer() == 42",),
    )

    synth = get_synthesizer("constant", value=42)
    candidate = synth.synthesize(task)[0]
    result = evaluate(task, candidate)
    print("passed:", result.passed)


if __name__ == "__main__":
    main()
