# ADR-004: Require a Sanitized Evidence Boundary for Private Factory Intelligence

- Status: accepted and implemented
- Date: 2026-08-17

## Context

Governor needs evidence from a private software factory, but neither the Strands agent nor an
external intelligence provider should receive unrestricted repository access. Repository content
can contain proprietary code, personal paths, credentials, prompt injection, and narrative claims
that are not authorized policy.

The deterministic ALLOW, DENY, and ESCALATE gates must remain authoritative. Useful model analysis
must not weaken evidence, authority, permit, policy, validation, or scope requirements.

## Decision

All real-factory evidence crosses this local pipeline:

```text
fixed read-only source adapter
  -> RawEvidence (local only)
  -> deterministic classification and secret detection
  -> minimization and sanitization
  -> SanitizedEvidence
  -> deterministic external-intelligence policy
  -> Governor observation
  -> optional request-bound Strands/Codex advisory tool
```

`RawEvidence` and `SanitizedEvidence` are distinct frozen Pydantic models. Intelligence requests
require actual `SanitizedEvidence` instances and reject raw strings, dictionaries, raw evidence,
and policy-blocked evidence before a provider process can start.

## Classification

| Classification | External treatment |
|---|---|
| `PUBLIC` | Allowed when needed, with path privacy still applied |
| `INTERNAL` | Allowed only after minimization and sanitization |
| `CONFIDENTIAL` | Structural metadata only; free text and code are removed |
| `SECRET` | `BLOCK_EXTERNAL_EXPOSURE`; no statements or secret-derived hashes leave the boundary |

The policy is deterministic. A model cannot lower a classification or grant itself additional
context.

## Information and authority types

Evidence retains an explicit kind and trust level. `FACT`, `INFERENCE`, `POLICY`,
`HUMAN_DECISION`, and `MODEL_ADVISORY` are not interchangeable. Policy evidence requires an
authorized normative source. Human decisions require human-confirmed provenance. Model advisory
content remains descriptive and model-generated.

Repository prose is untrusted data. A README sentence using words such as “must” or “policy” cannot
be promoted into a Governor policy by an adapter or model inference.

## Local and external representations

`RawEvidence` is the local representation. Sensitive values use `SecretStr`, but masking is only a
defense in depth; raw objects still must not reach provider APIs or audit records.

`SanitizedEvidence` is the only external-eligible representation. It contains bounded statements,
logical resources, stable aliases, classifications, provenance, digests for deliberately removed
non-secret content, and redaction reasons. A separate boolean and action record whether external
processing is allowed.

## Read-only real factory adapter

`RealFactoryAdapter` reads a fixed allowlist of factory metadata and contract entrypoints. It never
recurses into application repositories, executes factory tools, reads source code, or writes under
the factory root. Governor receives the adapter through `FactoryEvidenceSource`, not through a
hard-coded path.

The adapter extracts aggregate readiness facts only. It does not implement the complete
`GovernanceSource` because the observed factory does not yet expose complete machine-readable
policy, capability, authority, and persistent permit registries. That absence produces
`INCOMPLETE_EVIDENCE` rather than invented defaults.

## First real observation

A real read-only factory observation completed locally. The factory Git status was identical before
and after extraction. Governor emitted sanitized aggregate evidence, no authoritative change
decision, and `INCOMPLETE_EVIDENCE`. One opt-in Codex invocation received only that sanitized
payload and returned an `ADVISORY_ONLY` evidence-backed risk report. Audit artifacts were written
outside the factory and were not committed.

## Why not direct repository access?

Direct access would make scope dependent on model behavior, expose unrelated content, weaken path
confinement, and turn prompt instructions into a privacy convention. A fixed local adapter makes
the permitted source set inspectable and testable.

## Why not send full code to Codex?

Most governance questions need relationships, counts, ownership facts, change categories, hashes,
or validator results rather than complete implementation text. Full code would expand proprietary
exposure and prompt-injection surface without granting Governor additional authority.

## Why typed sanitized evidence?

The type boundary prevents accidental substitution of file handles, paths, raw text, or arbitrary
dictionaries. Schema validation also preserves provenance, classification, and the deterministic
external-processing decision through every downstream consumer.

## Why a deterministic external policy?

Privacy is an authority decision. Allowing the model to decide whether it may see more data would
be circular and fail open under prompt injection or uncertainty.

## Consequences

Benefits:

- privacy controls are code and tests rather than prompt conventions;
- Codex remains subordinate and receives only request-bound structured evidence;
- Governor can observe a real factory without modifying it;
- public tests remain offline and use synthetic factories and fake providers;
- missing governance contracts are reported honestly.

Costs and limitations:

- the detector is a bounded safety layer, not a complete DLP product;
- deterministic aliases are stable but vulnerable to dictionary guessing for predictable names;
- classification correctness still depends on trusted local adapters and human policy;
- the real factory cannot produce a complete change decision until missing registries exist;
- source contracts and Codex CLI compatibility must be revalidated when either changes.

## Rejected alternatives

- Give Strands or Codex a repository path: rejected because scope and privacy would be model-driven.
- Send complete files after a warning: rejected because warnings do not enforce minimization.
- Use prompt-only redaction: rejected because untrusted content can influence the model.
- Treat narrative documentation as policy: rejected because description is not delegated authority.
- Invent default authority or permits for the real factory: rejected because Governor fails closed.
