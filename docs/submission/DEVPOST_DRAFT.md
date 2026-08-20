# Governor Agent

## Tagline

**A governance control plane for AI-assisted software development — explicit authority, deterministic policy, evidence, and human escalation.**

## Inspiration / Problem

AI coding agents are becoming dramatically faster at producing software changes, but the mechanisms used to govern those changes have not scaled at the same rate.

A change can compile, pass tests, and still be wrong for the system.

It may violate:

* authority boundaries;
* ownership rules;
* permitted scope;
* architectural constraints;
* evidence requirements;
* or decisions that should remain human.

The problem is not simply whether an agent can complete a task.

The harder question is:

**Should this agent be allowed to complete this task, under these conditions, with this evidence?**

Governor Agent explores that governance layer.

## What it does

Governor Agent evaluates structured software-change requests before treating successful execution as sufficient evidence of correctness.

A builder proposes a change.

Governor uses a Strands Agent and narrowly scoped tools to inspect the request and trusted governance sources.

Deterministic gates then enforce:

* policy;
* authority;
* permits;
* scope;
* approved validators;
* evidence requirements.

The result is one of three explicit outcomes:

### ALLOW

The requested work is inside the actor's authority and permitted scope, and the required evidence is present.

### DENY

An objective governance rule has been violated.

The system rejects the work without asking an LLM to reinterpret the rule.

### ESCALATE

The system detects a legitimate decision that exceeds the agent's authority.

Instead of inventing an answer, Governor packages the available evidence, options, and risks for a human decision.

The model helps inspect and explain.

**The model does not own governance authority.**

## How Strands is used

Governor is built around one central Strands `Agent`.

The implementation uses:

* three request-bound custom tools;
* a system prompt with explicit trust and authority boundaries;
* a real Strands agent/tool loop;
* Pydantic structured output;
* typed hooks that record tool usage without exposing sensitive payloads;
* an injected `Model` boundary for deterministic offline testing and optional future model providers.

The agent can gather and interpret evidence, but the final governance decision must remain consistent with the deterministic domain rules.

If a model-generated report conflicts with the deterministic result, Governor rejects the report rather than allowing the model to override policy.

## Demonstrated scenarios

The public demo contains three reproducible synthetic scenarios.

### 1. Safe configuration change — ALLOW

A change is inside the permitted scope.

Required validators succeed.

The necessary evidence is present.

Governor returns:

`ALLOW`

No unnecessary human approval is required.

### 2. Permit scope violation — DENY

A docs-only permit is used for a request targeting production infrastructure.

Governor detects the scope violation before running validators and returns:

`DENY`

Passing tests cannot override an invalid permit.

### 3. Persistence ownership ambiguity — ESCALATE

The technical tests pass, but the proposed change introduces a second source of truth for persistent data.

The implementation may be technically possible, but ownership of persistence is an architectural decision outside the agent's authority.

Governor returns:

`ESCALATE`

and presents the human reviewer with explicit options and their associated risks.

## What we built

The contest-ready MVP includes:

* local CLI;
* Strands Agent loop;
* deterministic governance domain;
* synthetic software-factory environment;
* explicit permits and policies;
* approved validators;
* structured evidence;
* append-only audit records;
* audit digest verification;
* agent behavior evaluations;
* prompt-injection tests;
* path-safety tests;
* synthetic evidence and privacy scenarios;
* reproducible `ALLOW`, `DENY`, and `ESCALATE` demonstrations.

A privacy-preserving read-only adapter contract was also validated privately against pre-existing factory context.

That compatibility experiment is intentionally **not** part of the public demonstrated feature set and is not presented as production GoNucleo integration.

## Why this matters

Most agent systems focus on making agents more capable.

Governor focuses on a different problem:

**how much authority should an agent have?**

The goal is not maximum automation.

The goal is:

**maximum safe autonomy with minimum unnecessary human interruption.**

Routine work that is clearly authorized should not require a human to approve every step.

Forbidden work should fail deterministically.

Ambiguous or high-authority decisions should return to a human with useful evidence rather than being silently decided by a model.

This creates a possible governance layer between increasingly capable software agents and the systems they modify.

## Evidence and auditability

Governor records decisions as append-only audit records.

The project includes:

* structured governance outcomes;
* digest verification;
* tamper-detection checks;
* controlled validator execution;
* explicit authority and permit contracts;
* agent behavior evaluations;
* deterministic scenario expectations.

The public demo is designed to be reproducible without access to private systems or paid inference.

## Privacy and security model

The public contest demonstration uses a synthetic factory.

It does not require:

* private GoNucleo repositories;
* production systems;
* AWS credentials;
* paid inference;
* private Codex authentication.

The implementation follows a read-only-first and fail-closed approach.

Repository content is treated as untrusted data.

Secret values are excluded from prompts and audit logs.

The public scenarios use synthetic fixtures.

## Honest limitations

Governor Agent is an MVP and intentionally does not claim capabilities that were not demonstrated.

### Amazon Bedrock

An injectable Bedrock provider boundary exists, but Bedrock has **not been called or evaluated** as part of the demonstrated project.

It is not claimed as a demonstrated contest capability.

### AgentCore

AgentCore is **not implemented or demonstrated**.

### Real factory integration

The public demo does not operate on the private GoNucleo factory.

A read-only compatibility experiment and sanitized evidence boundary were validated privately, but they are not production integration and are not part of the public contest demonstration.

Complete machine-readable capability, policy, authority, and persistent permit contracts for governing a real software factory remain future work.

Governor currently has no authority to mutate real projects.

## Pre-existing work and provenance

Governor Agent is new hackathon-period work.

Its code, fixtures, schemas, tests, and project documentation were created during the hackathon period.

GoNucleo is pre-existing private software-factory context.

Living Memory is a separate pre-existing, all-rights-reserved project.

Neither codebase was copied into Governor Agent.

The GoNucleo Golden Path generated the initial project scaffold during the hackathon period, and that origin is explicitly documented in the project's provenance record.

## Testing

Judges can run the complete synthetic demonstration locally without an account, AWS credentials, private data, or paid inference.

Repository:

`https://github.com/gonuzzz-collab/governor-agent`

Clone the contest submission branch:

```bash
git clone --branch submission --single-branch https://github.com/gonuzzz-collab/governor-agent.git
cd governor-agent
uv sync --locked
```

Run the validation suite:

```bash
./scripts/validate
```

Run all three governance scenarios:

```bash
.venv/bin/governor --verbose agent-demo all
```

Run the agent behavior evaluation:

```bash
.venv/bin/governor eval-agent
```

Expected governance outcomes:

`ALLOW`
`DENY`
`ESCALATE`

The public demonstration uses an offline deterministic model to exercise the real Strands tool loop reproducibly.

## Built with

* Python
* Strands Agents SDK
* Pydantic
* uv
* GitHub Actions
* deterministic governance rules
* structured audit records
* synthetic test fixtures

## License

Governor Agent is distributed under the **Apache License 2.0**.

Third-party dependencies retain their respective licenses.

## Closing

AI agents are becoming capable enough to perform increasingly consequential software work.

Capability alone is not sufficient.

They also need explicit limits on:

* what they may do;
* what evidence they must provide;
* which decisions they may make;
* and when control must return to a human.

**Governor Agent is an experiment in making those boundaries executable.**
