# Free Testing Access

Status: draft pending a public repository URL.

Judges can run the complete synthetic demo without an account, credentials, network access after
installation, private data, AWS, or paid inference.

## Install

```bash
git clone <PUBLIC_REPOSITORY_URL>
cd governor-agent
uv sync --locked
```

Python 3.11 or newer and `uv` are required. A no-hardlink clean clone passed the locked quality gate
on Python 3.11.15 and 3.12.13; public CI repeats both versions after publication.

## Validate

```bash
./scripts/validate
```

This command runs locked Ruff checks and all deterministic, integration, security, scenario,
Strands, and agent-evaluation tests. Codex behavior is represented by fakes; the authenticated local
integration test is skipped. The gate needs neither AWS credentials nor a ChatGPT account.

Evidence-privacy and real-adapter tests create only temporary synthetic factories. They verify
classification, minimization, secrets, path confinement, audit redaction, and the sanitized-only
provider boundary without reading GoNucleo or any other private repository. The private/local
real-factory compatibility experiment is not part of the judging flow.

## Demonstrate

```bash
.venv/bin/governor --verbose agent-demo all
.venv/bin/governor eval-agent
```

Expected results are `ALLOW`, `DENY`, and `ESCALATE`, followed by a 9/9 evaluation report. The
offline model is clearly labeled and exists to exercise the real Strands tool loop reproducibly.

## Inspect automation output

```bash
.venv/bin/governor agent-demo all --format json
.venv/bin/governor --debug agent-demo safe
.venv/bin/governor verify-audit .governor/runs/<run-id>.json
```

No production system or private factory is required. Testing access will remain free through the
official judging period. Optional Bedrock execution, private Codex-account integration, and any
real-factory integration are not part of free judging access.
