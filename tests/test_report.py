"""Tests for report rendering."""

import json

from synthforge.loop import LoopConfig, solve_task
from synthforge.report import render_json, render_markdown, render_text, report_to_dict
from synthforge.synth.template import TemplateSynthesizer
from synthforge.types import Task


def _report():
    task = Task(
        task_id="add",
        prompt="return the sum of a and b",
        entry_point="add",
        tests=("assert add(1, 1) == 2",),
        signature="def add(a, b):",
    )
    return solve_task(task, TemplateSynthesizer(), config=LoopConfig(samples=1))


def test_render_text_mentions_status() -> None:
    text = render_text(_report())
    assert "add" in text
    assert "SOLVED" in text


def test_render_json_roundtrips() -> None:
    report = _report()
    payload = json.loads(render_json(report))
    assert payload["task_id"] == "add"
    assert payload["solved"] is True
    assert payload == report_to_dict(report)


def test_render_markdown_has_header_and_row() -> None:
    md = render_markdown([_report()])
    assert md.startswith("| task | status | tests | repairs |")
    assert "| add |" in md
