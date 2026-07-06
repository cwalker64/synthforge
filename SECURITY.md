# Security Policy

## Supported versions

synthforge is pre-1.0; only the latest release on the `main` branch receives
fixes.

## Reporting a vulnerability

Please report security issues privately via GitHub's **Report a vulnerability**
feature (Security → Advisories) rather than opening a public issue. I aim to
acknowledge reports within a few days.

## Scope and threat model

synthforge executes candidate code in a subprocess with a wall-clock timeout
and a reliability guard that disables obviously destructive calls. **This is not
a security sandbox.** It defends against accidental damage from a misbehaving
candidate, not against deliberately malicious code, which can still exhaust
resources or reach APIs the guard does not cover.

If you run untrusted or model-generated code with synthforge, run the whole
evaluator inside a container or virtual machine with no network and strict
resource limits. Bug reports that assume the guard is a real sandbox are out of
scope; reports of the guard failing to stop *accidental* damage are in scope.
