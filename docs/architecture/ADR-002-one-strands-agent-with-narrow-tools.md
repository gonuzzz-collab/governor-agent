# ADR-002: Use One Strands Agent with Narrow Tools

- Status: accepted
- Date: 2026-08-17

## Context

The MVP needs a genuine agent loop without premature coordination complexity. A generic shell tool
would expose unnecessary authority, while a multi-agent network would obscure the core governance
contract.

## Decision

Use one Strands `Agent` with request-bound custom tools for change inspection, governance
inspection, and deterministic evaluation. Add typed hooks for tool-name observability and validated
structured output. Tests use an explicitly labeled offline deterministic model; Bedrock is injected
through the Strands `Model` boundary.

## Consequences

The tool loop is inspectable, reproducible, and least-privilege. Real model behavior still requires
Bedrock evaluation before contest-ready claims can be made.
