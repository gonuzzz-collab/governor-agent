# ADR-001: Keep Governance Authority Outside the Model

- Status: accepted
- Date: 2026-08-17

## Context

Model reasoning is useful for selecting inspection tools and explaining ambiguity, but model output
is probabilistic and can be influenced by untrusted repository content. Permits, authority, scope,
required evidence, and validator outcomes must remain enforceable and testable.

## Decision

Hard governance is encoded in schema-validated policies and deterministic gates. The model cannot
grant authority, widen a permit, suppress evidence, or replace validator results. Every Strands
structured report is compared with the authoritative decision and rejected on conflict.

## Consequences

The system is more predictable and testable, and prompt injection cannot directly change hard
outcomes. The agent must maintain an explicit boundary between interpretation and authority.
