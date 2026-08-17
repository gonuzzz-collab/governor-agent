# Architecture Options

Decision date: 2026-08-17

## Decision

Choose a deterministic governance core with one Strands Governor agent and narrow read-only tools.
Policies, authority, permits, validators, and evidence remain outside the model. The model selects
tools, correlates evidence, explains results, and identifies ambiguity. Hard gates remain code.

## Option A: deterministic core plus one Strands agent

Status: CHOSEN

Flow:

    change request
          |
          v
    Strands Governor -> narrow inspection tools
          |
          v
    deterministic policy, authority, permit, scope and evidence gates
          |
          +---- safe and complete ----> ALLOW or CLOSE
          +---- objective violation --> DENY or VALIDATION_FAILED
          +---- human authority ------> ESCALATE

Benefits:

- Strands is central to tool selection and the real agent loop.
- The LLM cannot invent or override hard governance.
- Tests can exercise the domain without paid model calls.
- A provider boundary permits Bedrock and deterministic test models.
- The design supports a clear CLI and three short demo scenarios.

Costs:

- Requires a disciplined boundary between agent interpretation and deterministic decisions.
- Structured evidence must be designed before broad tool access.

## Option B: LLM-first code reviewer

Status: REJECTED

This would be fast to prototype but would collapse policy interpretation and authority into prose.
It would be difficult to test, unsafe under prompt injection, and insufficiently distinct from an AI
code reviewer.

## Option C: multi-agent governance network

Status: REJECTED FOR MVP

Multiple policy, security, evidence, and reviewer agents would add coordination failure modes without
improving the first vertical slice. The product needs one competent agent with purpose-built tools.

## Option D: reuse or rename Living Memory

Status: REJECTED

Living Memory predates the competition, is independently scoped, and has an all-rights-reserved
license. Its implementation will not be copied. It may later become an external evidence capability
through an explicit adapter and disclosure.

## Option E: deterministic CLI without Strands

Status: REJECTED AS FINAL ARCHITECTURE

A deterministic engine is necessary but not sufficient for the contest. It cannot demonstrate the
required Strands agent loop, contextual tool selection, or safe interpretation of ambiguous change
intent. It remains the testable core under Option A.

## Thirty-second architecture

A builder proposes a change. Governor uses Strands to inspect the change and consult explicit
governance sources such as policies, capabilities, authority, and permits. Deterministic gates
enforce hard rules. The agent gathers evidence and runs approved validators. Safe work continues
automatically, forbidden work is rejected, and architectural ambiguity is escalated to a human with
evidence.

## Main boundaries

### GovernanceSource

The core consumes an adapter contract, not factory paths. SyntheticFactoryAdapter is public and
first. RealFactoryAdapter is private-aware, read-only, and deferred.

### ModelProvider

The agent receives a configured Strands model. Production preference is Amazon Bedrock. Tests use a
deterministic model double and never require network or paid calls.

### Trusted and untrusted data

- System governance: trusted agent contract and non-overridable safety instructions.
- Trusted governance: explicitly configured policy, capability, authority, and permit sources.
- Untrusted project content: source, comments, README files, issues, diffs, and validator output.

Untrusted content can provide evidence but cannot instruct Governor or alter policy.

### Authority levels

The first implementation is Observer: inspection, evidence, decision record, and escalation package.
Auditor and Gatekeeper behavior may be added only after deterministic tests. Coordinator is not an
MVP requirement.

## First vertical slice

1. Parse a structured ChangeRequest.
2. Load a synthetic governance source.
3. Inspect requested files and permit.
4. Evaluate deterministic authority and scope gates.
5. Run an allowlisted validator.
6. Collect typed evidence.
7. Produce and persist a schema-validated GovernanceDecision.
8. Demonstrate safe, denied, and human-escalation outcomes.
9. Wrap the workflow with a real Strands Agent and custom tools.

## Decision consequences

- No generic shell tool.
- No web UI, database, RAG, vector store, MCP, or multi-agent system for the MVP.
- Audit records are local JSON with deterministic identifiers where possible.
- AgentCore evaluation occurs only after a local end-to-end demo is stable.
