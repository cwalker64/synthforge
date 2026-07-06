# Design notes

A collection of decisions and their rationale. These are opinions, not
promises; some may age badly.

## Offline-first, dependency-free

The reference synthesizer, evaluator and repairer are all pure standard
library. That was a deliberate constraint: evaluation results should be
reproducible on a laptop with no API keys, no model weights and no network. A
language-model-backed synthesizer is a natural extension — implement the
`Synthesizer` protocol and register it — but it lives outside the core so the
core stays testable and green in CI.

## The reliability guard is not a sandbox

`reliability_guard()` disables a handful of destructive calls (`os.remove`,
`subprocess.Popen`, `os.system`, ...) before candidate code runs, and the child
process is killed on timeout. This stops *accidents*, not a determined
adversary: a candidate can still exhaust memory or find a call we did not think
to disable. For genuinely untrusted code (e.g. real model output), run the
whole evaluator inside a container or VM. The subprocess boundary is there so
one bad candidate cannot take down the evaluator, not to contain malware.

## Repair as search, not understanding

The `RuleRepairer` does not "understand" a bug. It applies a small set of AST
operators (swap an arithmetic operator, flip a comparison, nudge an integer
literal) to produce single-edit neighbours of the failing program, then lets
the evaluator decide which — if any — improved. This is closer to mutation
search than to a reasoning agent, which keeps it deterministic and fast. It
solves the class of off-by-one and wrong-operator bugs and nothing cleverer;
that is by design.

## pass@k

We use the unbiased estimator from Chen et al. (2021), evaluated as a product
so we never build large binomial coefficients. When `k > n` the estimator is
undefined, so we fall back to the observed proportion and document it rather
than silently returning `1.0`.

## Immutable value objects

`Task`, `Candidate`, `EvalResult` and friends are frozen dataclasses. Results
flow one way through the pipeline; making them immutable removes a class of
"who mutated this?" bugs. `RunReport` is the exception — the loop accumulates
into it — and is intentionally left mutable.

## Open questions

- A cost model / budget for LLM-backed synthesizers.
- Confidence intervals on pass@k for small suites.
- Richer repair operators (guarding empty inputs, missing returns).
