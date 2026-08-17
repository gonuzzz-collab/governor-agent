# Amazon Bedrock AgentCore Evaluation

Last verified: 2026-08-17

Decision: **do not deploy yet**. Re-evaluate after one authorized Bedrock model passes the agent
behavior suite and an AWS budget is active.

## Material value

AgentCore Runtime could strengthen the submission with isolated sessions, immutable runtime
versions, stable endpoints, automatic scaling, and managed OpenTelemetry observability. It supports
Strands and direct Python code deployment.

Official sources:

- [How AgentCore Runtime works](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-how-it-works.html)
- [Direct Python code deployment](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-code-deploy-python.html)
- [AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-get-started.html)
- [AgentCore pricing](https://aws.amazon.com/bedrock/agentcore/pricing/)

## Minimal architecture if approved

```text
Judge or CLI client
        |
        v
AgentCore Runtime endpoint
        |
        v
Governor Strands Agent
        |
        +--> Amazon Bedrock model
        |
        +--> bundled synthetic factory (read-only)
        |
        +--> ephemeral decision result

Deployment artifact: CodeZip in S3
Observability: automatic OpenTelemetry to CloudWatch with conservative sampling
```

Do not add Gateway, Memory, Identity, Browser, Code Interpreter, MCP, a database, or a VPC for the
contest demo. None is required by the current workflow.

## Preferred deployment shape

- AgentCore direct code deployment (`CodeZip`) to avoid a container build and ECR.
- Python runtime compatible with the locked project and ARM64 dependencies.
- One runtime and the default endpoint only.
- Public network mode only if the runtime needs Bedrock; no access to the private factory.
- Synthetic fixture bundled with the artifact.
- Idle session timeout: 300 seconds.
- Maximum session lifetime: 1,800 seconds.
- Explicit `StopRuntimeSession` after testing where applicable.
- Full resource removal immediately after recording evidence unless live judging access is approved.

## Required implementation before deployment

1. Add `bedrock-agentcore` as an optional, pinned dependency.
2. Add a small runtime entrypoint with `/invocations` and `/ping` through the official SDK.
3. Accept only a scenario identifier or schema-validated request; never an arbitrary path.
4. Return the same structured decision and safe trace available locally.
5. Package without `.venv`, `.git`, `.governor`, caches, private adapter inputs, or local paths.
6. Test the entrypoint locally before creating AWS resources.
7. Run ARM64 dependency/package validation.
8. Add teardown verification for Runtime, endpoint, S3 artifact, logs/retention, and any role created.

## Human and security gates

- AWS account and Builder ID confirmed.
- Promotional credits requested or explicit non-credit spend accepted.
- Bedrock model and region selected with current price checked.
- Least-privilege deployment and runtime roles reviewed.
- Budget/alert active before the first call.
- Maximum authorized total test spend recorded.
- Public endpoint and judging-period lifetime explicitly approved.
- CloudWatch retention and trace sampling approved.

## Current blockers

- No AWS CLI or verified credentials.
- No confirmed credits, budget, region, or model access.
- No live Bedrock behavior evaluation.
- No authorization to create billable resources.

AgentCore is therefore a potentially valuable enhancement, not an MVP dependency and not an
implemented capability.
