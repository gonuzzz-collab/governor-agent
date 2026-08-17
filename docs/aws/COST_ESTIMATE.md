# AWS Cost Gate

Last verified: 2026-08-17

This is a planning estimate, not a bill or price guarantee. Recheck official pricing immediately
before authorization.

## AgentCore Runtime

The official pricing table listed active consumption at:

- USD 0.0895 per vCPU-hour;
- USD 0.00945 per GB-hour.

An intentionally conservative illustration assumes one full vCPU and 1 GB billed for an entire
60-second demo session, even though AWS states CPU I/O wait can be free when no background process
runs:

```text
runtime per session
= 60 / 3600 * (0.0895 + 0.00945)
= approximately USD 0.00165

20 sessions
= approximately USD 0.033 before other services
```

This is only the AgentCore Runtime component. It excludes:

- Amazon Bedrock model input/output tokens;
- S3 code artifact storage and requests;
- CloudWatch logs, traces, metrics, storage, queries, and optional masking;
- network transfer;
- failed deployments or unexpectedly long sessions;
- taxes and price/region changes.

## Proposed first-test ceiling

Recommended human authorization: **maximum USD 5 total** for the first Bedrock plus AgentCore
experiment, backed by an AWS Budget/alert and a same-session teardown. This is a proposed ceiling,
not authorization.

## Cost controls

- No Gateway, Memory, Browser, Code Interpreter, Evaluations, or Policy service in the first deploy.
- At most one runtime, one endpoint, and one S3 deployment artifact.
- Maximum 20 invocations.
- 300-second idle timeout and 1,800-second maximum lifetime.
- Stop active sessions after evidence capture.
- Remove runtime resources and S3 artifact immediately after testing.
- Verify CloudWatch retention and remaining artifacts.
- Record actual Cost Explorer/Billing evidence when available; never claim promotional credits as
  cash or as guaranteed coverage.

Official source: [Amazon Bedrock AgentCore pricing](https://aws.amazon.com/bedrock/agentcore/pricing/).
