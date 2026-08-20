# Regression Guard Report

Date: 2026-08-17

## Objective

Validate the Governor MVP after deterministic-domain, Strands, CLI, audit, evaluation, and real
factory inventory changes.

## Automated wrapper result

Status: **Not approved**.

The parent `regression-guard` wrapper resolved its helper commands under
`governor-agent/.skills/`. This isolated public repository intentionally has no private `.skills`
directory, so its critical `core-validate-root` step exited `127` before running. The failure is a
wrapper integration mismatch, not a test failure. It remains recorded as a failed gate.

## Substitute evidence

- Direct global `core-validate --root <governor-repository>`: PASS, exit `0`.
- Project `scripts/validate`: PASS.
- Unit, contract, integration, scenario, security, agent, and evaluation suite: 49 PASS.
- Ruff lint and format: PASS.
- Python bytecode compilation: PASS.
- Real CLI runtime: safe, deny, and escalation outcomes matched their contracts.
- Agent evaluation: 4/4 cases, zero false allow/deny in the fixture suite.
- Clean clone in `/tmp`: lock installation, validation, agent demo, and evaluations PASS.
- Current clean clone at `4248f08`: 103 tests, agent demo ALLOW/DENY/ESCALATE, evaluation 9/9,
  false allow/deny 0.000.
- Visual validation: not applicable; product is CLI-only.
- Docker/runtime rebuild: not applicable; no container or service exists.

## Regressions discarded

- Deterministic permit, scope, authority, validator, and evidence behavior remained green.
- Strands tool order and structured-output consistency remained green.
- Prompt-injection fixture did not alter governance authority.
- Audit tampering and symlink escapes were rejected.
- Standalone clone does not require private factory tooling.

## Open risk

The parent Regression Guard wrapper cannot natively validate an isolated public repository without
assuming private `.skills` content. Copying or symlinking that tooling into Governor would violate
the public/private boundary. A future parent-tooling change may add a standalone mode, but that is
outside Governor's repository.

## Final assessment

**Approved with risks.** The implemented project gates and independent clean-clone evidence pass;
the shared Regression Guard wrapper itself remains incompatible and must not be reported as passed.
