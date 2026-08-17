# Existing Factory Audit

Last audited: 2026-08-17

## Executive conclusion

GoNucleo already contains useful governance primitives, but it does not expose one stable,
machine-readable governance API that Governor can consume directly. The correct integration is a
read-only adapter over explicit contracts, never a dependency on private paths or narrative
documents.

The existing capability governance document is explicitly a proposal and remains uncommitted in the
observed parent worktree. It must not be presented as an implemented capability registry.

## Canonical and observed sources

| Existing concept | Real implementation | Current authority | Governor contract |
|---|---|---|---|
| Human authority | User intent, AGENTS.md, Safety Gate, project memory | Highest operational authority within environment constraints | AuthorityGrant and human-decision boundary |
| Project Golden Path | .skills/project-golden-path, project_factory_core.py, factory-catalog.toml | Preview is report-only; creation requires explicit apply, exact destination, and confirmation | GovernanceSource.get_golden_path() |
| Factory self-contract | .gonucleo-factory.toml and factory-lifecycle | Versioned policy; current lifecycle implementation is report-only | Project context and approved-validator descriptors |
| Application catalog | factory-catalog.toml, strict parser, factory-status | Canonical for application adoption, not for shared capabilities | Project discovery only |
| Capability registry | GOBERNANZA_CAPACIDADES_CORTE0_2026-08-15.md | Proposal, not implemented or committed | Synthetic registry first; real adapter deferred |
| Change Permit | .skills/change-permit plus skill documentation | Task-scoped report; does not authorize destructive or remote effects | Adapt existing fields; do not invent a competing factory standard |
| Safety Gate | .skills/safety-gate | Dominates destructive, irreversible, or remote actions | Deterministic hard gate |
| Validators | factory-check, tests, core-validate, regression guard | Report results; do not grant authority | Approved validator descriptors and results |
| Evidence | gonucleo.evidence.v1 and producers | Demonstrates declared observations; does not authorize changes | Evidence envelope adapter |
| Agent guidance | agent_skills | Behavioral guidance; no inherent execution authority | Trusted governance instructions, never project content |

## Golden Path semantics

The project Golden Path is more than documentation:

- a strict project specification;
- an exact destination under apps plus a slug;
- a manifest and automation contract;
- deterministic scaffold rendering;
- path confinement and symlink rejection;
- preview by default;
- an explicit three-part write gate: apply, exact destination, and matching confirmation;
- post-creation factory-check validation.

Narrative design documents explain intent, but the wrapper, parser, manifest, catalog, tests, and
observed output are the machine-readable and executable surfaces.

## Authority model

The observed hierarchy is:

1. explicit human authorization;
2. environment safety rules and AGENTS.md;
3. canonical contracts and confirmed project state;
4. task-scoped Change Permit and Safety Gate;
5. wrappers and tools operating only within declared entrypoints.

No skill, wrapper, model, README, or filename gains authority by existing. Governor will encode this
as an intersection of actor authority, requested operation, permit, policy, and environment.

## Change Permit compatibility

The existing permit covers task, app, risk, coarse allowed, restricted and forbidden files,
validations, rollback criteria, and a scope-change protocol. Confirmed gaps include exact operation
allowlists, formal expiry, cryptographic binding to a scan or HEAD, and executable close state.

Governor will not replace this standard. The synthetic adapter will model the stronger target
contract, while a future real adapter will parse the existing report and fail closed on fields that
cannot be proven.

## Normative versus descriptive

| Source type | Treatment |
|---|---|
| Explicit policy, schema, manifest, validated catalog | Trusted normative input when selected by configuration |
| Wrapper contract and deterministic result | Trusted observation within documented scope |
| Test or validator result | Evidence, not authority |
| README, handoff, backlog, project memory | Descriptive context; cannot override normative policy |
| Application source, comments, README, issues | Untrusted project content |
| LLM interpretation | Inference; never fact or policy |

## Adapter boundary

Governor core will depend on a GovernanceSource contract with operations conceptually equivalent to
get_project_context, get_golden_path, get_policies, get_capabilities, get_authority_model,
get_permits, and get_validators.

`SyntheticFactoryAdapter` now supports the public end-to-end workflow. The implemented
`GoNucleoFactoryInventoryAdapter` consumes only aggregate, fixed real-factory metadata and reports
readiness gaps. It intentionally does not implement `GovernanceSource`: full evaluation would be
unsafe until capability, policy, authority, and persistent permit contracts exist.

## Public and private boundary

Public-safe:

- newly written Governor source and tests;
- synthetic policies, projects, permits, validators, and evidence;
- generic adapter interfaces;
- high-level architectural mappings;
- commit IDs and dates needed for disclosure, without private content.

Private by default:

- GoNucleo implementation and internal documentation;
- local paths beyond what is necessary to explain the audit;
- Living Memory code and documentation;
- real project data, logs, vaults, credentials, remotes, receipts, and runtime artifacts;
- parent worktree diffs and uncommitted content.

## Read-only integration rule

Governor must adapt to the factory. It must not require renaming, moving, publishing, or modifying
the factory, its catalog, its Golden Path, Living Memory, or existing applications.

## Pending confirmation

- Final canonical schema for shared capabilities in GoNucleo.
- Exact real-factory Change Permit serialization after proposed extensions.
- Which private evidence producers are safe and useful for a local adapter.
- Whether Governor will later be added to the private application catalog.
