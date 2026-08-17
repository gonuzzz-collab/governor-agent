# Local End-to-End Demo

This demo is synthetic but genuinely executed. It never accesses the private GoNucleo factory.

## Setup

```bash
uv sync --locked
./scripts/validate
```

## Run

```bash
.venv/bin/governor --verbose agent-demo all
```

Expected sequence for every case:

1. Strands selects `inspect_change_request`.
2. Strands selects `inspect_governance`.
3. Strands selects `evaluate_change_request`.
4. Deterministic gates run approved validators only when eligible.
5. Strands emits schema-validated `AgentGovernanceReport`.
6. Governor verifies that the model report exactly matches deterministic authority.
7. Governor leaves an append-only, digest-bearing decision record.

## Expected outcomes

| Scenario | Technical validation | Governance outcome | Human interruption |
|---|---|---|---|
| Safe | PASS | `ALLOW` | No |
| Permit scope violation | Not run | `DENY` | No |
| Second persistence source | PASS | `ESCALATE` | Yes, with options and risks |

The escalation is the main narrative: passing tests do not resolve ownership of a source of truth.
Governor refuses to invent that authority.

## Inspect evidence

```bash
.venv/bin/governor --debug agent-demo safe
.venv/bin/governor verify-audit .governor/runs/<run-id>.json
.venv/bin/governor eval-agent
```

Use `--format json` for automation. Individual deny and escalation commands intentionally return
non-zero exit codes; `agent-demo all` returns zero when all expected outcomes match.
