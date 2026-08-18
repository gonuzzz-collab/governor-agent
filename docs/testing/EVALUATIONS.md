# Agent Evaluations

Status: implemented and demonstrated offline on 2026-08-17.

The core suite runs through the real Strands `Agent` and its custom-tool loop. It uses the labeled
deterministic model double so every clone can reproduce results without credentials, network access,
or paid inference. It does not claim to measure a Bedrock model.

```bash
uv sync --locked
.venv/bin/governor eval-agent
```

The versioned suite is [core_suite.json](../../evals/core_suite.json). It covers safe autonomous
closure, deterministic denial before validators, human escalation after technical validation, and
prompt injection in untrusted request content.

## Metrics

The report records decision accuracy, exact Strands tool-selection accuracy, escalation accuracy,
policy grounding, evidence completeness, false allow, false deny, hallucinated policies, and
unnecessary human interruption.

The initial four-case baseline produced 4/4 passing cases, `1.000` decision/tool/policy/evidence
metrics, and `0.000` false allow, false deny, hallucinated policy, and unnecessary-interruption
rates. These are fixture-suite results, not general production performance claims.

Each run appends its report under `.governor/evaluations/`. Evaluation changes require a suite
version change when expected behavior changes materially.

## Codex intelligence boundary

The Codex adapter is outside the authoritative decision suite. Unit tests inject a fake subprocess
runner and verify the exact least-privilege command, environment allowlist, structured schema,
authority separation, invalid-output failure, and sanitized errors without Codex or network access.

The authenticated test is intentionally opt-in:

```bash
env \
  GOVERNOR_RUN_CODEX_INTEGRATION=1 \
  GOVERNOR_CODEX_HOME=/absolute/path/to/chosen-codex-home \
  PYTHONPATH=src \
  .venv/bin/python -m unittest tests.integration.test_codex_local_opt_in
```

It uses only the fixed synthetic risk-analysis request. Public CI must not set these variables or
depend on a contributor's ChatGPT account. A skipped local integration test is the expected default
result.
