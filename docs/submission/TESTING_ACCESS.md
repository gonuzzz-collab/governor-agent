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

Python 3.11 or newer and `uv` are required. The tested clean-clone environment used Python 3.12.

## Validate

```bash
./scripts/validate
```

## Demonstrate

```bash
.venv/bin/governor --verbose agent-demo all
.venv/bin/governor eval-agent
```

Expected results are `ALLOW`, `DENY`, and `ESCALATE`, followed by a 4/4 evaluation report. The
offline model is clearly labeled and exists to exercise the real Strands tool loop reproducibly.

## Inspect automation output

```bash
.venv/bin/governor agent-demo all --format json
.venv/bin/governor --debug agent-demo safe
.venv/bin/governor verify-audit .governor/runs/<run-id>.json
```

No production system or private factory is required. Testing access will remain free through the
official judging period. Optional Bedrock execution is not part of free judging access.
