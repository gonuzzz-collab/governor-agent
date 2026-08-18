# Real Factory Adapter Boundary

Status: sanitized read-only evidence extraction implemented; complete `GovernanceSource`
integration remains intentionally blocked.

`RealFactoryAdapter` reads only fixed metadata and contract entrypoints. It does not recurse through
applications, read source files, execute factory tools, inspect credentials or logs, access runtime
data, or write under the factory root. The compatibility name
`GoNucleoFactoryInventoryAdapter` remains available.

Governor consumes the adapter through `FactoryEvidenceSource`. Concrete factory paths remain inside
the adapter and the CLI composition root.

## Real source inventory

| Factory source | Fixed relative location | Format | Machine-readable | Role | Classification | Adapter status | Sanitization |
|---|---|---|---|---|---|---|---|
| Factory self manifest | `.gonucleo-factory.toml` | TOML | Yes | Normative for declared identity/automation | INTERNAL | Aggregate fields implemented | Required |
| Project catalog | `.skills/factory-catalog.toml` | TOML | Yes | Normative for listed adoption/portfolio facts | INTERNAL | Aggregate counts implemented | Required |
| Golden Path | `.skills/project-golden-path` | Executable contract | No standalone data schema | Normative for scaffolding only | INTERNAL | Source readiness and adoption facts implemented; complete policy adapter deferred | Required |
| Project state | `.skills/factory-status` | Executable JSON report | Yes at runtime | Descriptive derived state | INTERNAL | Presence/readiness implemented; tool execution intentionally omitted | Required |
| Agent policies | `AGENTS.md` | Markdown | No | Normative for agents, not a typed Governor policy registry | INTERNAL | Presence only; policy translation blocked | Required |
| Capability registry | No registry | Absent | No | Normative registry missing | CONFIDENTIAL | Fail closed | Required if introduced |
| Capability analysis | `docs/fabrica_aplicaciones/GOBERNANZA_CAPACIDADES_CORTE0_2026-08-15.md` | Markdown | No | Descriptive/unclosed | CONFIDENTIAL | Presence only; never treated as authority | Required |
| Change Permit tool | `.skills/change-permit` | Executable report | Yes at runtime | Normative workflow, no persistent permit registry | INTERNAL | Presence/readiness implemented; persistent adapter blocked | Required |
| Persistent permit registry | No registry | Absent | No | Normative registry missing | CONFIDENTIAL | Fail closed | Required if introduced |
| Authority registry | No registry | Absent | No | Normative registry missing | CONFIDENTIAL | Fail closed | Required if introduced |
| Validator declarations | `.gonucleo-factory.toml` `[automation]` | TOML | Yes | Normative but factory-local | INTERNAL | Readiness only; approved-validator registry deferred | Required |
| Evidence contract | `docs/fabrica_aplicaciones/schemas/gonucleo.evidence.v1.schema.json` | JSON Schema | Yes | Normative interchange contract | INTERNAL | Presence/readiness implemented | Required |
| Safety Gate | `.skills/safety-gate` | Executable report | Yes at runtime | Normative command-risk gate, not actor authority | INTERNAL | Presence/readiness implemented | Required |
| Architecture | `project_memory/ARCHITECTURE.md` | Markdown | No | Descriptive | CONFIDENTIAL | Presence only; raw prose excluded | Required |

The inventory is also machine-readable through `inspect-factory`; it records readiness, format,
machine readability, normative/descriptive role, classification, adapter need, and sanitization
need for every source.

## Normative versus descriptive

Normative authority is explicit and source-specific. Executable Golden Path behavior can govern
scaffolding, but it is not automatically a general change policy. Factory status and architecture
documents describe observed state. The capability analysis is not a registry. Neither Governor nor
Codex may promote descriptive prose into policy.

## Golden Path analysis

Confirmed machine-readable facts are catalog adoption state and the project automation manifests.
The Golden Path executable and tests define scaffolding behavior, but no standalone schema maps
that behavior into Governor policies, authority, or permits. The minimal adapter therefore exposes
only aggregate adoption and source readiness. It does not redesign or interpret the Golden Path.

## Capability resolution

The observed factory has no complete authority-bearing capability registry implementing
`resolve_capability(id, version)`. The existing analysis remains descriptive. Governor reports the
registry as missing instead of loading all tooling or fabricating a `Capability` object. A future
adapter should resolve one exact ID/version from a reviewed machine-readable registry.

## Change Permit compatibility

The existing report-only workflow and Governor models overlap but are not interchangeable:

| Existing Change Permit field/report section | Governor field | Current compatibility |
|---|---|---|
| Task | `ChangeRequest.objective` | Conceptual mapping only |
| App/type/risk | project, action/scope, `risk_level` | Requires a typed schema |
| Allowed files | `ChangePermit.allowed_paths` | Compatible concept; needs validated relative-path data |
| Allowed/forbidden changes | `allowed_actions` / `forbidden_actions` | Compatible concept; vocabulary mapping missing |
| Required validations | `validators` / `evidence_required` | Compatible concept; approved IDs missing |
| User approval flag | Human authorization evidence | Not an actor authority grant |
| Expiry/status/actor/capability | Required Governor fields | Not fully represented persistently |

Because the missing fields are authority-bearing, the adapter does not manufacture defaults.

## Sanitized observation flow

```text
FactoryEvidenceSource.collect_evidence()
  -> RawEvidence (aggregate local facts)
  -> EvidenceSanitizer
  -> SanitizedEvidence
  -> RealFactoryObservationRunner
  -> INCOMPLETE_EVIDENCE or human-safe next step
  -> optional ADVISORY_ONLY Codex analysis
```

Audit output is required to live outside the real factory. An audit path under the factory root is
rejected before directory creation.

## First real case

The first observation used the real fixed source set and no application content. It produced one
sanitized aggregate evidence object and deterministically reported incomplete governance evidence.
One opt-in Codex call analyzed that object only. The factory Git status was unchanged before and
after both local extraction and the evidence review workflow.

```bash
governor inspect-factory-evidence /path/to/factory \
  --audit-dir /safe/path/outside/factory \
  --format json
```

Optional Codex analysis additionally requires both `--codex-home` and `--allow-codex`. The command
returns the normal `INCOMPLETE_EVIDENCE` exit code while mandatory registries remain unavailable;
an advisory report cannot change that status.
