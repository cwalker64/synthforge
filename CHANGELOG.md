# Changelog

All notable changes to this project are documented here. The format is loosely
based on [Keep a Changelog](https://keepachangelog.com/), and the project aims
to follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-07-07

First tagged release.

### Added

- `Task` / `TaskSuite` model and JSONL suite loader, with a bundled example suite.
- Subprocess sandbox with wall-clock timeout and a reliability guard.
- Test-based evaluator producing `EvalResult`, and the `pass@k` / `mean_pass@k`
  metrics.
- Reference synthesizers: `template` (prompt-driven), `fixture` (replay), and
  `perturb` (seed mutation), resolvable through a registry.
- AST repair operators and the `RuleRepairer` search.
- `solve_task` control loop tying synthesis, evaluation and repair together.
- Report rendering as text, JSON and Markdown.
- `synthforge` command-line interface (`run`, `synths`).
- Documentation, runnable examples, and CI (lint, format, type-check, tests
  across Python 3.9-3.13).

[Unreleased]: https://github.com/cwalker64/synthforge/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/cwalker64/synthforge/releases/tag/v0.1.0
