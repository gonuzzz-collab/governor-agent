# Provenance and Eligibility Record

Last audited: 2026-08-17

## Eligibility boundary

The official Submission Period begins 2026-08-10 09:00 Pacific Time and ends 2026-09-14 17:00
Pacific Time. Governor Agent is a new repository and project created during that window. Existing
GoNucleo and Living Memory work is not relabeled as Governor work.

Git history is primary evidence. Filesystem timestamps are secondary evidence only for uncommitted
material and are never used to imply authorship or eligibility.

## PRE-EXISTING WORK

| Component | Origin or repository | Approximate origin | Initial observed evidence | Nature | Directly reused? | Disclosure | Eligibility risk |
|---|---|---:|---|---|---|---|---|
| GoNucleo monorepo | Private parent repository | 2026-03-13 or earlier | Root commit 2431b80a338965c8c5e6f33295f9527123d71f23 | Existing software factory and applications | No code | Yes, as external context | High if submitted; not submitted |
| Safety Gate, Change Permit, workflow orchestrator | GoNucleo parent | 2026-05-19 | 08f62beb2df349791359e167b77a805ef840a277 | Existing governance tooling | No code | Yes, conceptual antecedent and future adapter target | High if copied; avoided |
| Living Memory product | Independent local repository under apps/living-memory | 2026-07-22 | b78a016639a5ed637a3c157951d36a9af994a5c0 | Evidence-backed technical memory product | No | Mandatory antecedent disclosure | High; all-rights-reserved and pre-period |
| Living Memory prototype | GoNucleo tools/living_memory_prototype | 2026-07-21 | e0bf0b25ed7fe7456bdc110a8ef20c77af254fa4 | Earlier scanner and evidence prototype | No | Mandatory if ever incorporated | High; proprietary evaluation notice |

Living Memory's observed license explicitly grants no open-source reuse rights. Governor therefore
does not copy its code, algorithms, fixtures, schemas, prose, tests, or generated assets. Generic
ideas such as evidence, hashes, scanning, and provenance are antecedent concepts only.

## HACKATHON-PERIOD WORK

These components were created during the period but belong to the existing factory, not
automatically to Governor:

| Component | Repository | First observed commit | Date | Reuse decision | Disclosure risk |
|---|---|---|---:|---|---|
| Declarative application Golden Path | GoNucleo parent | 324b324fb0276afd48552603001ad56abd4ce74c | 2026-08-12 | Interface and placement observed; no code copied | Disclose generated scaffold |
| Golden Path automation v1 | GoNucleo parent | 2627e80c4e43281df1560efcb985b8134539d291 | 2026-08-14 | Generated baseline scaffold used | Disclose generated origin |
| Factory self-lifecycle foundation | GoNucleo parent | 83373ab5d5cc49f159c1263b45c8f8ab7426c132 | 2026-08-16 | Architecture observed; no code copied | Avoid claiming as Governor |

The factory's eligibility as a standalone entry remains unproven and irrelevant to the chosen
submission boundary: the submission is Governor, not the factory.

## STANDARD LIBRARIES OR FRAMEWORKS

| Component | Source | Version or status | Nature | Disclosure |
|---|---|---|---|---|
| Python | Python Software Foundation | Project floor planned at 3.10 or newer | Standard language and runtime | Normal dependency disclosure |
| Strands Agents SDK | Strands Agents and AWS | 1.52.0 observed 2026-08-17 | Required open-source agent framework, Apache-2.0 | Pin version and link official docs |
| Pydantic | Pydantic maintainers | 2.13.4 observed 2026-08-17 | Structured validation dependency, MIT | Pinned runtime dependency |
| Hatchling | PyPA | 1.32.0 observed 2026-08-17 | Reproducible build backend, MIT | Pinned build dependency |
| Python standard library | Python Software Foundation | Runtime-provided | Standard library | No special pre-existing disclosure |
| Apache License 2.0 | Apache Software Foundation | 2.0 | Project license text | Required public license |

Additional dependencies must be added only when implemented and recorded with exact versions.

## NEW GOVERNOR WORK

| Component | Repository | Created | Initial evidence | Status |
|---|---|---:|---|---|
| Governor Agent repository | apps/governor-agent independent Git repository | 2026-08-17 | Initial commit `9a4bdcf` | New hackathon work |
| Phase 0 audit and architecture boundary | Governor repository | 2026-08-17 | Initial commit `9a4bdcf` | New hackathon work |
| Deterministic governance domain | Governor repository | 2026-08-17 | Commit `5d28337` | New hackathon work |
| Synthetic factory, validators, audit trail and CLI demos | Governor repository | 2026-08-17 | This increment's next commit | New hackathon work |
| Strands agent and agent evaluations | Governor repository | Not yet implemented | Future commits only | Planned |

## UNCERTAIN OR NEEDS REVIEW

- The parent repository contains multiple root histories and refs. The earliest observed root proves
  pre-existence but does not reconstruct every component's complete ancestry.
- Several factory documents and evidence modules are untracked. Their filesystem birth times fall
  inside the period, but they have no Git provenance and will not be incorporated.
- Some factory capabilities were introduced in commits during the period. Their ownership and exact
  eligibility do not make them Governor work.
- Public hosting URL, public repository creation time, and submission ownership remain pending.

## Reuse policy

1. Prefer a new, small Governor implementation.
2. Use synthetic public fixtures.
3. Reference private factory concepts only through a generic adapter contract.
4. Record every future imported snippet, asset, algorithm, or schema before incorporation.
5. Never rewrite history or timestamps to alter provenance.
6. Keep the parent repository and Living Memory out of Governor commits.

## Evidence queries

The audit used root-commit enumeration, commit counts around the boundary, path-addition history,
tags, branches, independent-repository history, tracking status, and license inspection. The
observed parent history contained 909 commits before the boundary and 15 commits from the boundary
to audit time. Those counts include all reachable refs and are contextual, not a legal conclusion.
