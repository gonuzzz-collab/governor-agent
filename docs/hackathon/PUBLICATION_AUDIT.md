# Publication Audit

Last reviewed: 2026-08-17

Status: automated local review passed; publication remains blocked on human privacy, ownership, and
IP approval.

No repository was published and no remote was changed during this review.

## Scope

The review covered the tracked worktree and the complete independent Governor Git history through
the pre-audit baseline `da4f025`. The resulting audit-only documentation and public-script message
changes were rescanned before commit. No tracked file was deleted during either interval, so the
current-file content scan covers every historical path reviewed.

## Automated observations

| Check | Result | Evidence |
|---|---|---|
| Personal absolute paths and local username | PASS | No local home, mounted-workspace, or username match |
| Common credential values | PASS | No AWS access key, private-key header, or credential-assignment pattern match |
| Sensitive filenames | PASS WITH EXPECTED FILE | Only `.env.example`; it contains instructions and no variable values |
| Deleted historical files | PASS | No path returned by the full-history deletion query |
| Binary or oversized tracked artifacts | PASS | Text-only source/docs/fixtures; largest tracked blob is the dependency lock below 200 KiB |
| Private runtime evidence | PASS | `.governor/`, virtual environments, caches, and local audit runs are ignored |
| Public fixture boundary | PASS | Demo policy, project, requests, permits, validators, and evidence are synthetic |

These are heuristic checks, not credential revocation evidence or a substitute for provider-side
secret scanning.

The README body and all submission documentation are English. Seven Spanish README section labels
remain because the current private Golden Path validator treats those exact labels as a
machine-checked project contract; changing them made the strict factory gate fail. Governor adapts
to that contract rather than mutating the private factory.

## License observations

- Governor declares Apache-2.0 and includes the full license text.
- No third-party source, model output, binary, asset, or Living Memory material is vendored.
- Direct packages: Strands Agents is Apache-2.0, Pydantic is MIT, and development-only Ruff is MIT.
- Installed transitive metadata declares permissive licenses except Certifi's MPL-2.0 file-level
  license; the project imports the package normally and does not copy or modify it.
- `uv.lock` is the canonical version inventory. Package metadata was inspected from the locked
  Python 3.12 environment.

This is an engineering compatibility review, not legal advice. Final IP acceptance remains human.

## Intentional antecedent disclosures requiring human review

`PROVENANCE.md` names GoNucleo and Living Memory and records dates and private-history commit IDs to
defend hackathon eligibility. The public synthetic demo does not require their code or data, but the
owner must approve disclosure of those identifiers. The project manifest also names GoNucleo as
owner and currently classifies the repository as `internal`; changing that classification is part
of the human publication gate.

## Publication gate

Before creating or exposing a remote repository, a human must:

1. approve the antecedent names, dates, commit identifiers, and owner label for public disclosure;
2. confirm ownership of all new Governor work and accept Apache-2.0 distribution;
3. run the final secret/privacy review against the exact publication commit;
4. explicitly authorize repository publication.

Until all four actions are complete, Governor remains a local, unpublished repository.
