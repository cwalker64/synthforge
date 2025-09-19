"""A deterministic, offline template synthesizer.

Rather than call a language model, this backend maps a task onto a small
library of code *templates*. The template is chosen from an explicit
``hints["kind"]`` when present, and otherwise inferred from keywords in the
prompt. It is intentionally simple - it exists so the whole synth -> eval ->
repair pipeline can run with zero dependencies - but it genuinely solves the
common "toy" tasks (identity, arithmetic, reductions, string ops).
"""

from __future__ import annotations

import re
from typing import Callable

from synthforge.synth.base import AbstractSynthesizer
from synthforge.types import Candidate, Task

_SIGNATURE_RE = re.compile(r"def\s+(?P<name>\w+)\s*\((?P<params>[^)]*)\)")


def parse_signature(signature: str, fallback_name: str) -> tuple[str, list[str]]:
    """Return ``(function_name, [param, ...])`` parsed from a ``def`` header."""
    match = _SIGNATURE_RE.search(signature or "")
    if not match:
        return fallback_name, []
    name = match.group("name")
    params = []
    for raw in match.group("params").split(","):
        token = raw.strip()
        if not token or token in {"*", "/"}:
            continue
        token = token.split(":")[0].split("=")[0].strip().lstrip("*")
        if token:
            params.append(token)
    return name, params


def render(name: str, params: list[str], body: str) -> str:
    """Assemble a runnable function definition from a one-expression body."""
    args = ", ".join(params) if params else "*args"
    return f"def {name}({args}):\n    return {body}\n"


# Each template turns the parsed parameter list into a return expression.
TEMPLATES: dict[str, Callable[[list[str]], str]] = {
    "identity": lambda p: (p[0] if p else "args[0]"),
    "sum": lambda p: (" + ".join(p) if p else "sum(args)"),
    "product": lambda p: (" * ".join(p) if p else "__import__('math').prod(args)"),
    "difference": lambda p: (" - ".join(p[:2]) if len(p) >= 2 else "args[0] - args[1]"),
    "maximum": lambda p: (f"max({', '.join(p)})" if p else "max(args)"),
    "minimum": lambda p: (f"min({', '.join(p)})" if p else "min(args)"),
    "length": lambda p: (f"len({p[0]})" if p else "len(args[0])"),
    "reverse": lambda p: (f"{p[0]}[::-1]" if p else "args[0][::-1]"),
}

# Prompt keywords that hint at a template. Order matters: earlier wins.
_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("identity", ("unchanged", "identity", "itself", "as is", "as-is")),
    ("sum", ("sum", "add", "total", "plus")),
    ("product", ("product", "multiply", "times")),
    ("difference", ("difference", "subtract", "minus")),
    ("maximum", ("maximum", "largest", "greater", "max ")),
    ("minimum", ("minimum", "smallest", "least", "min ")),
    ("length", ("length", "count", "number of", "how many")),
    ("reverse", ("reverse", "reversed", "backwards")),
]


def infer_kind(prompt: str) -> str | None:
    """Guess a template name from the words in ``prompt``."""
    text = prompt.lower()
    for kind, needles in _KEYWORDS:
        if any(needle in text for needle in needles):
            return kind
    return None


class TemplateSynthesizer(AbstractSynthesizer):
    name = "template"

    def synthesize(self, task: Task, n: int = 1) -> list[Candidate]:
        name, params = parse_signature(task.signature or "", task.entry_point)
        ordered = self._candidate_kinds(task)
        candidates: list[Candidate] = []
        for kind in ordered:
            template = TEMPLATES[kind]
            source = render(name, params, template(params))
            candidates.append(
                Candidate(source, origin=self.name, metadata={"kind": kind})
            )
            if len(candidates) >= n:
                break
        return candidates or [Candidate(render(name, params, "None"), origin=self.name)]

    def _candidate_kinds(self, task: Task) -> list[str]:
        """Return template names to try, most-likely first."""
        preferred = task.hints.get("kind") or infer_kind(task.prompt)
        order: list[str] = []
        if preferred in TEMPLATES:
            order.append(preferred)
        # Fill remaining slots with the rest of the library for variety.
        for kind in TEMPLATES:
            if kind not in order:
                order.append(kind)
        return order
