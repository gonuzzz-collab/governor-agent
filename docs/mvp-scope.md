# Governor Agent — Hackathon MVP Scope

## Goal

Build one working governance agent with Strands Agents SDK that evaluates a proposed software change and returns one of three controlled outcomes:

- `ALLOW`
- `BLOCK`
- `ESCALATE`

The decision must be based on explicit policy, declared authority/scope, and supplied validation evidence.

## Target user

Software professionals and teams using AI coding agents who need a lightweight governance checkpoint before accepting or advancing an automated change.

## End-to-end user story

> As a software professional supervising AI-assisted changes, I provide Governor Agent with a change proposal, the actor's declared authority, a policy, and validation evidence. Governor Agent evaluates the proposal and returns an auditable decision telling me whether the change may proceed, must be blocked, or needs human judgment.

## Required MVP capabilities

1. Load one declarative policy file.
2. Load one change proposal.
3. Load or receive validation evidence.
4. Invoke a Strands-based Governor Agent.
5. Evaluate authority and target scope.
6. Evaluate explicit policy constraints.
7. Evaluate whether required evidence is present.
8. Return exactly one controlled decision: `ALLOW`, `BLOCK`, or `ESCALATE`.
9. Produce a human-readable decision record with reasons and relevant evidence references.
10. Demonstrate all three outcomes with synthetic scenarios.

## Decision contract

Every result must contain at least:

```json
{
  "decision": "ALLOW | BLOCK | ESCALATE",
  "summary": "human-readable explanation",
  "policy_reasons": [],
  "evidence_considered": [],
  "human_action_required": false
}
```

`human_action_required` must be `true` for `ESCALATE`.

## Demo scenarios

### Scenario A — ALLOW

A documentation-only change is proposed in an allowed path. The actor has authority for that scope and required checks pass.

Expected decision: `ALLOW`.

### Scenario B — BLOCK

An agent proposes modifying a protected deployment/security target that is explicitly outside its authority.

Expected decision: `BLOCK`.

### Scenario C — ESCALATE

A change touches a high-impact dependency or architectural boundary for which the policy requires human approval or available evidence is insufficient.

Expected decision: `ESCALATE`.

## Explicitly out of scope for the MVP

- autonomous execution of approved code changes;
- unrestricted shell access;
- integration with private GoNucleo tooling;
- integration with private Living Memory internals;
- integration with Lexidiam internals;
- enterprise RBAC;
- a general-purpose policy language;
- production identity/authentication systems;
- automatic GitHub merge authorization;
- full CI/CD governance;
- large multi-agent orchestration;
- broad repository architecture inference.

These may be future directions, but adding them during the hackathon would weaken the core demonstration.

## Definition of done

The MVP is considered complete when:

- the project installs from documented instructions;
- Strands Agents SDK is genuinely used in the decision workflow;
- all three demo scenarios run end-to-end;
- outputs conform to the controlled decision contract;
- tests cover the three decision classes and important invalid inputs;
- the architecture diagram matches the implemented system;
- the README distinguishes verified functionality from future work;
- a reproducible demo can be recorded in under five minutes.
