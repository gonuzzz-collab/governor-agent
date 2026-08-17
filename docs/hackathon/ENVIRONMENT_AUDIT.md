# Environment Audit

Last audited: 2026-08-17 (America/Santiago)

## Scope

This audit records the local build environment available before Governor Agent was created. It does
not prove that any cloud account, credential, remote repository, or deployed service exists.

## Confirmed facts

| Area | Observed state | Consequence |
|---|---|---|
| Factory root | Private parent GoNucleo working tree | Existing factory is an upstream, read-only integration target. |
| Governor root | Independent repository under apps/governor-agent | New repository created through the factory Golden Path. |
| Parent Git | `master`, latest observed commit `6189301` dated 2026-08-16 | Parent history is not Governor history. |
| Parent worktree | Dirty with multiple unrelated user changes and untracked blocks | Never stage, clean, reset, or commit from the parent repository. |
| Python | CPython 3.14.4 | Project metadata must retain the upstream-supported floor rather than require this host version. |
| Package tooling | `uv 0.11.7` | Use a project-local `.venv` and lock file; do not install globally. |
| Git | 2.53.0 | Sufficient for an isolated repository and provenance audit. |
| Strands Agents | Not installed globally | Install only in Governor's local environment. |
| Current Strands release | `strands-agents 1.52.0`, Python `>=3.10`, Apache-2.0; released 2026-08-12 | Pin this observed release for the first reproducible increment. |
| AWS CLI | Not installed | Local MVP and tests cannot depend on AWS CLI. |
| AWS credentials | Unavailable through the observed CLI path | Bedrock and AgentCore remain explicitly unverified and disabled. |
| Existing project scanner | Available at the parent factory | Scanner was used only for discovery; it is not a Governor dependency. |

## Workspace topology

The parent monorepo contains applications, shared code, project memory, agent skills, deterministic
wrappers, and factory documentation. Relevant independent Git repositories include Living Memory and
several application repositories. Governor is intentionally another independent repository under
`apps/`, matching the established local organization while keeping public history separate.

## Operational constraints

- The real factory and Living Memory remain read-only.
- No AWS deployment, paid model call, remote mutation, publication, commit in the parent repository,
  or credential inspection is authorized by this audit.
- The local MVP must be runnable with deterministic test doubles and synthetic fixtures.
- The parent worktree's existing changes belong to the user and are outside Governor's scope.

## Evidence commands

Evidence was gathered with read-only commands including `git status`, `git log`, `git rev-list`,
`git ls-files`, `python3 --version`, package metadata inspection, `uv --version`, Golden Path preview,
factory checks, and scoped file searches. Secret values were never printed.

## Pending confirmation

- Exact Linux distribution details were not material to project placement or eligibility.
- AWS account, region, model access, billing controls, and credentials require human action.
- Public Git hosting and the final clone URL do not exist yet.
