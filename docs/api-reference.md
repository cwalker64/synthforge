# API reference

The public surface is intentionally small. Everything below is importable from
the top-level `synthforge` package unless noted.

## Types

### `Task`
Frozen dataclass describing a synthesis problem.

| field | type | notes |
|-------|------|-------|
| `task_id` | `str` | unique id |
| `prompt` | `str` | natural-language description |
| `entry_point` | `str` | name of the function under test |
| `tests` | `tuple[str, ...]` | assert-style snippets |
| `signature` | `str \| None` | optional `def ...:` header |
| `setup` | `str` | code prepended before the candidate |
| `reference` | `str \| None` | optional canonical solution |
| `hints` | `dict[str, Any]` | backend-specific hints |
| `timeout` | `float` | per-test wall-clock limit (s) |

### `Candidate`
`source: str`, `origin: str`, `metadata: dict`.

### `EvalResult`
Holds `outcomes: tuple[TestOutcome, ...]`, `timed_out`, `duration`, and derived
properties `passed`, `num_passed`, `num_tests`, `pass_rate`, `first_error()`.

### `RunReport`
`attempts: list[EvalResult]`, `repairs: list[RepairStep]`, with `solved` and
`best` properties.

## Functions

### `solve_task(task, synthesizer, *, repairer=None, config=None) -> RunReport`
Run the full synth → eval → repair loop. `config` is a `LoopConfig`.

### `evaluate(task, candidate, *, timeout=None) -> EvalResult`
Score a single candidate against a task in the sandbox.

### `load_suite(path) -> TaskSuite`
Load a JSONL suite. `synthforge.tasks.load_example_suite()` loads the bundled one.

## Protocols

### `Synthesizer`
`name: str` and `synthesize(task, n=1) -> list[Candidate]`. Built-ins:
`TemplateSynthesizer`, `FixtureSynthesizer`, `PerturbSynthesizer`. Resolve by
name via `synthforge.synth.registry.get_synthesizer`.

### `Repairer`
`name: str` and `repair(ctx: RepairContext) -> list[Candidate]`. Built-in:
`RuleRepairer`.

## Metrics

`synthforge.eval.metrics.pass_at_k(num_samples, num_correct, k) -> float` and
`mean_pass_at_k(per_task, k) -> float`.

## Reporting

`synthforge.report.render_text / render_json / render_markdown`.
