# Governor Agent

Governor is a governance agent for AI-assisted software factories.

Status: deterministic local workflow demonstrated. The Strands tool loop is the next increment, so
this revision is not yet the contest-ready agent.

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

Run all three public scenarios:

    .venv/bin/governor --verbose demo all

Evaluate one structured request and emit automation-friendly JSON:

    .venv/bin/governor evaluate \
      fixtures/demo_factory/scenarios/safe.json \
      --factory fixtures/demo_factory \
      --format json

Individual scenario exit codes are `0` for allowed work, `3` for human escalation, `4` for denial,
`5` for incomplete evidence, `6` for validation failure, and `2` for invalid input. `demo all`
returns zero only when all three outcomes match their declared demonstration contract.

## Validar

    ./scripts/doctor
    ./scripts/test
    ./scripts/validate
    ./scripts/evidence --format json

The default suite is offline and makes no paid model call. It validates domain rules, schema
contracts, approved validator execution, audit persistence, and all three end-to-end scenarios.

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

## License

Apache-2.0. Third-party dependencies retain their own licenses.

## Implemented boundary

- Implemented and demonstrated: typed domain, deterministic gates, synthetic factory adapter,
  approved validators, append-only local audit records, CLI, and safe/deny/escalate scenarios.
- Next: a real Strands `Agent` with purpose-built tools and a deterministic offline model double.
- Planned: read-only private factory adapter, agent evaluations, and optional AgentCore assessment.
