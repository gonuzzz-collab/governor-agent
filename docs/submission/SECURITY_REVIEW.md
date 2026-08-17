# Security Review

Status: local MVP review completed 2026-08-17; cloud and publication reviews remain pending.

## Controls implemented

- Observer mode: no governed-project mutation or deployment.
- No generic shell tool exposed to the model.
- Request-bound tools accept no model-selected filesystem path.
- Lexical traversal checks plus filesystem symlink confinement.
- Trusted governance is schema-validated and size-limited.
- Repository/request content is labeled untrusted data.
- Permit, authority, scope, evidence, and validator gates are deterministic.
- Missing authority/evidence fails closed.
- Approved validator kinds use fixed arguments and `shell=False`.
- Validator raw output is excluded from agent and audit output.
- Strands structured reports must exactly match deterministic authority.
- Audit records are append-only, digest-bearing, and independently verifiable.
- Real factory inventory uses fixed paths, no recursive application scan, aggregate output, and no
  project identifiers or absolute paths.
- Bedrock execution requires explicit `--allow-paid-inference` acknowledgement.
- Public CI grants only `contents: read`, pins third-party actions by commit digest, and makes no
  cloud deployment or paid inference call.

## Tests observed

Traversal, symlink escape, malformed policy, expired/missing permit, scope violation, low authority,
validator failure, missing evidence, prompt injection, model override, audit tampering, and CLI exit
behavior are covered. The full suite passed 49 tests in the clean-clone rehearsal.

After that rehearsal, three additional failure-recovery integrations raised the development-tree
suite to 52 passing tests. The same locked gate passes locally on Python 3.11 and 3.12; a final clean
clone rehearsal remains required after committing the CI increment.

## Open risks

- A real Bedrock model has not been evaluated for tool-selection or prompt-injection behavior.
- No AWS credentials, region, guardrail, budget, or telemetry export has been configured.
- No AgentCore runtime or cloud cleanup procedure exists.
- Public-repository privacy/IP review has not occurred.
- Audit digests detect modification but are not signatures and do not prove author identity.
- The shared Regression Guard wrapper is incompatible with this standalone repo; direct critical
  validation passed, but the wrapper's own result remains not approved.
