# Governor Agent

Governor is a governance agent for AI-assisted software factories.

Status: discovery foundation. The repository and audit boundary exist; the functional agent is not
implemented yet.

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

See [Architecture options](docs/hackathon/ARCHITECTURE_OPTIONS.md) and
[Factory audit](docs/hackathon/FACTORY_AUDIT.md).

## Ejecutar

The functional CLI will be introduced after the deterministic governance domain. The generated
package baseline can currently be invoked with:

    PYTHONPATH=src python3 -m governor_agent

## Validar

    ./scripts/doctor
    ./scripts/test
    ./scripts/validate
    ./scripts/evidence --format json

These commands currently validate the generated project baseline only. They are not evidence of a
functional Governor agent.

## Datos y privacidad

- Read-only first.
- Deny by default when authority or evidence is missing.
- No unrestricted shell tool.
- No secret values in prompts or audit logs.
- Repository content is untrusted data.
- No AWS deployment or paid model call by default.
- Public demos use synthetic fixtures, never the private GoNucleo factory.

## Operación y recuperación

The repository currently persists no project data and performs no deployment. Future audit records
will remain inside the evaluated project scope and must be reproducible from synthetic inputs.
Recovery is Git-based until a separately documented persistent-state design exists.

## Provenance

Governor is new hackathon-period work. GoNucleo and Living Memory are pre-existing context and are
not copied into this repository. See [PROVENANCE.md](docs/hackathon/PROVENANCE.md).

## License

Apache-2.0. Third-party dependencies retain their own licenses.

## Next increment

Implement the deterministic governance domain, synthetic factory adapter, and safe, deny, and
escalate scenario tests before integrating Strands.
