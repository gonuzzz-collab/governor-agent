# Devpost Submission Draft

Status: draft; not submitted.

## Project name

Governor Agent

## Tagline

An agentic governance control plane for AI-assisted software development.

## Problem

AI coding agents dramatically increase software change velocity, but human governance does not
scale at the same rate. A change can compile and pass tests while violating authority, ownership,
permitted scope, evidence requirements, or architectural policy.

## Solution

Governor operationalizes explicit software governance. A builder proposes a structured change.
Governor uses Strands to inspect the request and trusted governance sources through purpose-built
tools. Deterministic gates enforce hard policy, authority, permit, scope, validator, and evidence
rules. Safe work closes automatically, objectively forbidden work is rejected, and architectural
ambiguity is escalated to a human with evidence, options, and risks.

## How Strands is used

- one central Strands `Agent`;
- three request-bound custom tools;
- system prompt with explicit trust and authority boundaries;
- real agent/tool loop;
- Pydantic structured output using the current invocation API;
- typed hooks that record tool names without sensitive payloads;
- injected `Model` boundary for deterministic offline testing and optional Amazon Bedrock.

The model does not own governance. Governor rejects any model-authored report that conflicts with
the deterministic decision.

## Demonstrated scenarios

1. Safe configuration change: validators pass and Governor returns `ALLOW` without a human.
2. Permit scope violation: a docs-only permit targets production infrastructure and Governor returns
   `DENY` before running validators.
3. Persistence ownership ambiguity: tests pass, but a second source of truth triggers `ESCALATE`
   with three explicit human options and their risks.

## Impact

Governor helps developers, architects, and small teams supervise routine agent-produced changes
without making a human re-review every safe operation. Its goal is maximum safe autonomy with
minimum unnecessary human interruption.

## What is implemented

Local CLI, Strands agent loop, deterministic governance domain, synthetic factory, permits,
policies, approved validators, evidence, append-only audit records, digest verification, agent
evaluations, prompt-injection/path-safety tests, and synthetic evidence/privacy scenarios. A
privacy-preserving read-only adapter contract was validated privately/local against pre-existing
factory context, but is excluded from the public demonstrated feature set.

## Honest limitations

The public demo uses only a synthetic factory and deterministic offline model. Amazon Bedrock
provider injection exists but has not been called or evaluated and is not claimed as demonstrated.
AgentCore is not implemented or demonstrated. The real-factory adapter and sanitized evidence were
privately validated as read-only compatibility experiments only; they are not production GoNucleo
integration or part of the public contest demo. Complete capability, policy, authority, and
persistent permit contracts for governing a real factory remain absent, as does any real-project
mutation authority.

## Pre-existing work disclosure

Governor Agent and its code, fixtures, schemas, tests, and documentation were created during the
hackathon period. GoNucleo is a pre-existing private software-factory context. Living Memory is a
separate pre-existing, all-rights-reserved project. Neither codebase was copied into Governor.
The GoNucleo Golden Path generated the initial project scaffold during the period; that origin is
disclosed in PROVENANCE.md.
