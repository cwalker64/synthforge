# Architecture

synthforge is organised as a short pipeline with three swappable stages plus a
thin orchestration layer. Everything is pure-Python and offline; the reference
backends never touch the network.

```
        Task ─► Synthesizer ─► [Candidate ...] ─► Evaluator ─► EvalResult
                                                       │
                                                       ▼  (if failing)
                                                    Repairer ─► [Candidate ...]
                                                       │
                                                       └──────► re-evaluate ...
```

## Modules

| Module | Responsibility |
|--------|----------------|
| `synthforge.types` | Immutable value objects: `Task`, `Candidate`, `TestOutcome`, `EvalResult`, `RepairStep`, `RunReport`. |
| `synthforge.tasks` | Build and validate tasks; load JSONL suites; the bundled example suite. |
| `synthforge.synth` | The `Synthesizer` protocol and reference backends (`template`, `fixture`, `perturb`) plus a registry. |
| `synthforge.eval` | The subprocess `sandbox`, the `runner` that scores a candidate, and `metrics` (`pass@k`). |
| `synthforge.repair` | The `Repairer` protocol, AST `operators`, and the `RuleRepairer` search. |
| `synthforge.loop` | `solve_task` — ties synth → eval → repair together into a `RunReport`. |
| `synthforge.report` | Render a `RunReport` as text, JSON or Markdown. |
| `synthforge.config` | `RunConfig` loading from mappings, JSON or a tiny `key: value` format. |
| `synthforge.cli` | The `synthforge` command-line entry point. |

## Data flow

1. A **`Task`** carries a natural-language `prompt`, an `entry_point` name, a
   tuple of `tests` (Python snippets that assert on the entry point), and
   optional `signature`/`hints`.
2. A **`Synthesizer`** turns the task into one or more **`Candidate`** programs.
3. The **evaluator** concatenates candidate + setup + each test and runs it in
   an isolated subprocess, returning an **`EvalResult`**.
4. If nothing passes, a **`Repairer`** proposes edited candidates from the
   failing one; the loop re-evaluates them within a repair budget.
5. Everything is recorded in a **`RunReport`**.

## Why a subprocess

Candidate code is arbitrary. Running it in-process risks corrupting the
evaluator (or worse). The evaluator therefore spawns a child process with a
wall-clock timeout and a reliability guard that disables obviously destructive
calls. See [design-notes.md](design-notes.md) for the threat model and its
limits.
