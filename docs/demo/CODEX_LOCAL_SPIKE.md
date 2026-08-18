# Local Codex Intelligence Spike

Status: implemented and demonstrated with an explicitly selected private Codex profile on
2026-08-17. The command is opt-in and advisory only.

This spike demonstrates:

```text
Governor -> Strands custom tool -> codex exec -> structured architectural-risk report
```

It does not evaluate a real repository, alter a governance decision, call Bedrock, use an OpenAI
API key, or belong in the default test suite.

## Prerequisites

Install a documented Codex CLI version compatible with the command flags and authenticate the
profile through ChatGPT. Select the profile by its absolute `CODEX_HOME`; do not copy or expose its
credential file.

Verify the chosen profile without printing credentials:

```bash
env CODEX_HOME=/absolute/path/to/chosen-codex-home codex login status
```

The expected status is a ChatGPT login. Governor also forces the ChatGPT login method at runtime and
does not forward `OPENAI_API_KEY`.

## Run the fixed synthetic spike

```bash
.venv/bin/governor codex-spike \
  --codex-home /absolute/path/to/chosen-codex-home \
  --allow-codex \
  --format json
```

`--allow-codex` is mandatory because the invocation consumes local Codex account quota. Expected
output has this Governor-owned boundary:

```json
{
  "authority": "ADVISORY_ONLY",
  "provider": "codex-exec",
  "report": {
    "summary": "...",
    "risks": [
      {
        "risk": "...",
        "evidence": ["..."]
      }
    ]
  },
  "schema_version": "governor.intelligence.v1",
  "strands_tool": "analyze_architectural_risks"
}
```

There is intentionally no ALLOW, DENY, ESCALATE, permission, authority, policy, or permit field in
the model-authored report.

## Safety properties

The implementation uses a temporary workspace, read-only sandbox, no approval path, ephemeral
session, ignored private configuration and rules, disabled shell/web/image/subagent tools, a
minimal child environment, strict JSON Schema output, timeout, output bound, and sanitized provider
errors. Evidence is labeled untrusted.

The model request still leaves the machine for Codex service processing. Supply only the minimum
sanitized evidence required for the question. Never include secrets, credentials, raw private
factory content, or a private repository path.

## Tests

Default unit and scenario tests use a fake provider and require neither Codex nor internet access.
The local integration test is skipped unless both opt-in variables are present:

```bash
env \
  GOVERNOR_RUN_CODEX_INTEGRATION=1 \
  GOVERNOR_CODEX_HOME=/absolute/path/to/chosen-codex-home \
  PYTHONPATH=src \
  .venv/bin/python -m unittest tests.integration.test_codex_local_opt_in
```

Never configure those variables in public CI. See
[ADR-003](../architecture/ADR-003-private-codex-intelligence.md) for the evaluated alternatives and
decision.
