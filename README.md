# Governor Agent

Governor is a governance agent for AI-assisted software factories.

Status: local Strands agent workflow implemented and demonstrated with an offline deterministic
model double. Amazon Bedrock support is implemented but deliberately untested until credentials and
cost authorization exist. This revision is an MVP, not yet the hardened contest submission.

## Propósito

AI coding agents increase software change velocity faster than human governance can scale. A change
can pass tests and still violate ownership, authority, architectural policy, permitted scope, or
evidence requirements.

Builders optimize for completing a change. Governor optimizes for preserving the system.

## Contrato de producto

- Audience: developers, architects, makers, and small teams using coding agents.
- Outcome: evaluate a structured change request end to end, gather evidence, enforce objective
  constraints, and continue, deny, or escalate.
- Track: Professional Agents.
- Maturity: experiment.
- Interface: CLI first.
- Deployment: local first.

## Arquitectura inicial

A builder proposes a change. A Strands Agent selects narrow inspection tools and consults explicit
governance sources. Deterministic gates enforce policy, authority, permit, scope, validator, and
evidence rules. Safe changes continue, forbidden changes are rejected, and decisions beyond the
agent's authority are escalated to a human with evidence.

The LLM is not the governance authority.

See the [architecture diagram](docs/architecture/ARCHITECTURE.md),
[architecture options](docs/hackathon/ARCHITECTURE_OPTIONS.md), and
[Factory audit](docs/hackathon/FACTORY_AUDIT.md).

## Ejecutar

Create an isolated environment and install exactly the locked dependencies:

    uv sync --locked

Run all three public scenarios through the real Strands agent loop:

    .venv/bin/governor --verbose agent-demo all

This offline command uses Strands `Agent`, custom tools, hooks, and structured output without
network access or paid inference. `governor demo all` remains available to exercise only the
deterministic layer.

Measure the agent against the versioned behavior suite:

    .venv/bin/governor eval-agent

Verify one append-only decision record:

    .venv/bin/governor verify-audit .governor/runs/<run-id>.json

Inspect only aggregate, fixed metadata from a local GoNucleo factory:

    .venv/bin/governor inspect-factory /path/to/gonucleo

Evaluate one structured request and emit automation-friendly JSON:

    .venv/bin/governor evaluate \
      fixtures/demo_factory/scenarios/safe.json \
      --factory fixtures/demo_factory \
      --format json

Individual scenario exit codes are `0` for allowed work, `3` for human escalation, `4` for denial,
`5` for incomplete evidence, `6` for validation failure, and `2` for invalid input. `demo all`
returns zero only when all three outcomes match their declared demonstration contract.

Use `--verbose` before the subcommand for validator and Strands tool names. Use `--debug` for safe
policy, evidence, decision, and digest identifiers; raw repository and validator output remains
excluded. Use `--format json` for structured automation output.

## Validar

    ./scripts/doctor
    ./scripts/test
    ./scripts/validate
    ./scripts/evidence --format json

The default suite is offline and makes no paid model call. It validates domain rules, schema
contracts, approved validator execution, audit persistence, the real Strands tool loop, structured
output consistency, prompt-injection resistance, and all three end-to-end scenarios.

The public CI workflow runs the locked gate and agent evaluation on Python 3.11 and 3.12. Its
third-party actions are pinned by commit digest and its token has read-only repository permission.

## Datos y privacidad

- Read-only first.
- Deny by default when authority or evidence is missing.
- No unrestricted shell tool.
- No secret values in prompts or audit logs.
- Repository content is untrusted data.
- No AWS deployment or paid model call by default.
- Public demos use synthetic fixtures, never the private GoNucleo factory.

## Operación y recuperación

Governor is currently an Observer. It does not mutate the governed project or deploy anything. Each
run appends a digest-bearing JSON record under `.governor/runs/`; prior runs are never overwritten.
Raw validator output is withheld from audit logs. Delete local demo evidence only when it is no
longer required; source recovery remains Git-based.

## Provenance

Governor is new hackathon-period work. GoNucleo and Living Memory are pre-existing context and are
not copied into this repository. See [PROVENANCE.md](docs/hackathon/PROVENANCE.md).

See [Local demo](docs/demo/LOCAL_DEMO.md) and [Agent evaluations](docs/testing/EVALUATIONS.md) for
reproducible evidence.

Judging drafts: [free testing access](docs/submission/TESTING_ACCESS.md),
[five-minute video plan](docs/submission/VIDEO_PLAN.md), and
[security review](docs/submission/SECURITY_REVIEW.md).

## License

Apache-2.0. Third-party dependencies retain their own licenses.

## Implemented boundary

- Implemented and demonstrated: typed domain, deterministic gates, synthetic factory adapter,
  approved validators, append-only local audit records, CLI, safe/deny/escalate scenarios, and a
  real Strands `Agent` tool loop with structured output and tool hooks.
- Implemented but not remotely demonstrated: injected Amazon Bedrock provider. The CLI requires
  `--allow-paid-inference` before it can make a Bedrock call.
- Implemented and demonstrated hardening: versioned agent evaluations, audit digest verification,
  tamper detection, and safe normal/verbose/debug output.
- Implemented and locally demonstrated: privacy-preserving real-factory inventory adapter. Full
  governance evaluation remains fail-closed until the factory defines machine-readable capability,
  policy, authority, and persistent permit contracts.
- Implemented and demonstrated hardening: required-validator failures become audited, fail-closed
  decisions; locked static checks and the full suite pass on Python 3.11 and 3.12.
- Assessed and deferred: optional AgentCore Runtime deployment until Bedrock behavior, identity,
  budget, and explicit spend gates are resolved.
- Next: authorized Bedrock behavior evaluation and public-repository privacy/IP review.
