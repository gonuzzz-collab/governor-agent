# Governor Agent

Governor is a governance agent for AI-assisted software factories.

Status: local Strands governance workflow implemented and demonstrated offline using the synthetic
factory. A Codex CLI advisory boundary and sanitized real-factory observation were validated only as
private/local, strictly read-only compatibility experiments; neither is part of the public contest
demonstration or production GoNucleo integration. Amazon Bedrock remains optional and deliberately
untested until credentials and cost authorization exist. This revision is the contest-ready MVP
submission candidate.

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

The LLM is not the governance authority. Optional intelligence is behind a separate advisory
boundary: private runtime can use an explicitly selected ChatGPT-authenticated Codex CLI, while a
public contest runtime may use Bedrock only after its independent credential and spend gates.

See the [architecture diagram](docs/architecture/ARCHITECTURE.md),
[private intelligence ADR](docs/architecture/ADR-003-private-codex-intelligence.md),
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

Run the fixed, read-only Codex intelligence spike only with an explicitly chosen authenticated
profile and quota acknowledgement:

    .venv/bin/governor codex-spike \
      --codex-home /absolute/path/to/chosen-codex-home \
      --allow-codex \
      --format json

The spike sends only synthetic evidence and returns an `ADVISORY_ONLY` architectural-risk report.
It does not read the repository or alter ALLOW/DENY/ESCALATE. See the
[local Codex spike guide](docs/demo/CODEX_LOCAL_SPIKE.md).

Private/local compatibility experiment only (not part of the public contest demonstration): extract
a real-factory readiness observation without exposing project content:

    .venv/bin/governor inspect-factory-evidence /path/to/factory \
      --audit-dir /safe/path/outside/factory \
      --format json

The expected current result is `INCOMPLETE_EVIDENCE`, not an ALLOW/DENY decision. Add
`--codex-home` and `--allow-codex` only when the sanitized payload should be analyzed using local
Codex quota. See the [privacy model](docs/security/EVIDENCE_PRIVACY_MODEL.md) and
[ADR-004](docs/architecture/ADR-004-sanitized-evidence-boundary.md).

Measure the agent against the versioned behavior suite:

    .venv/bin/governor eval-agent

Verify one append-only decision record:

    .venv/bin/governor verify-audit .governor/runs/<run-id>.json

Private/local compatibility experiment only (not part of the public contest demonstration): inspect
only aggregate, fixed metadata from a local GoNucleo factory:

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

Codex unit tests use a fake process provider. The authenticated local integration is opt-in and is
never required by public CI.

The public CI workflow runs the locked gate and agent evaluation on Python 3.11 and 3.12. Its
third-party actions are pinned by commit digest and its token has read-only repository permission.

## Datos y privacidad

- Read-only first.
- Deny by default when authority or evidence is missing.
- No unrestricted shell tool.
- No secret values in prompts or audit logs.
- Repository content is untrusted data.
- No AWS deployment or paid model call by default.
- No credential file is read, copied, logged, placed in fixtures, or committed.
- Codex receives only a Governor-selected structured evidence package and has advisory authority.
- Raw and sanitized evidence are separate types; deterministic policy blocks SECRET exposure.
- Real-factory extraction uses a fixed read-only allowlist and writes audit records outside the factory.
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
[security review](docs/submission/SECURITY_REVIEW.md). Publication remains gated by the
[local privacy and IP audit](docs/hackathon/PUBLICATION_AUDIT.md).

## License

Apache-2.0. Third-party dependencies retain their own licenses.

## Implemented boundary

- Implemented and demonstrated: typed domain, deterministic gates, synthetic factory adapter,
  approved validators, append-only local audit records, CLI, safe/deny/escalate scenarios, and a
  real Strands `Agent` tool loop with structured output and tool hooks.
- Validated experimentally in private/local runtime only (not public contest demonstration): a purpose-built Strands
  intelligence tool backed by stable `codex exec`, existing ChatGPT authentication, explicit
  `CODEX_HOME`, disabled execution/search tools, read-only sandbox, and schema-validated advisory
  output. Default tests use fakes and the local integration test is opt-in.
- Demonstrated publicly: typed PUBLIC/INTERNAL/CONFIDENTIAL/SECRET evidence, deterministic
  external-processing policy, path/identifier privacy, bounded secret detection, synthetic
  evidence/privacy scenarios, and redacted evidence audit.
- Validated experimentally in private/local runtime only: sanitized-only Codex requests and a
  fixed-source, strictly read-only real-factory observation adapter. This compatibility experiment
  is not the public contest demonstration and is not production GoNucleo integration.
- Implemented but not remotely demonstrated: injected Amazon Bedrock provider. The CLI requires
  `--allow-paid-inference` before it can make a Bedrock call.
- Implemented and demonstrated hardening: versioned agent evaluations, audit digest verification,
  tamper detection, and safe normal/verbose/debug output.
- Validated experimentally in private/local runtime only: privacy-preserving real-factory inventory
  adapter. Full governance of a real factory remains fail-closed until that factory defines
  machine-readable capability, policy, authority, and persistent permit contracts.
- Implemented and demonstrated hardening: required-validator failures become audited, fail-closed
  decisions; locked static checks and the full suite pass on Python 3.11 and 3.12.
- Assessed and deferred: optional AgentCore Runtime deployment until Bedrock behavior, identity,
  budget, and explicit spend gates are resolved.
- Assessed and deferred: direct Codex MCP consumption after the local locked-version spike exposed
  notification/result interoperability errors; custom model provider and experimental app-server
  integration add unnecessary coupling for this slice.
- Implemented for the public synthetic demo: `authorities.json` is a versioned
  `governor.authority-registry.v1` contract with one unique, explicit grant per actor.
  The real factory remains unchanged and fail-closed: a separate human decision and read-only
  adapter design are required before any real authority source is introduced. Bedrock and
  publication remain closed.
