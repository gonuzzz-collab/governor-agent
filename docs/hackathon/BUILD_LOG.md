# Hackathon Build Log

The log records Governor work only. Existing factory and Living Memory activity is documented in
PROVENANCE.md instead of being presented as Governor progress.

## 2026-08-17 - Discovery and isolated project foundation

- Commit: `9a4bdcf` (`chore: initialize governor project`).
- Goal: establish eligibility, factory boundary, official requirements, and safe repository location.
- Result: Phase 0 audits completed; Golden Path scaffold created and validated; independent Git
  repository initialized.
- Tests: parent factory-check strict passed with 3 OK, 0 WARN, 0 FAIL.
- Important decision: deterministic governance core plus one Strands agent; synthetic public factory
  before any real private adapter.
- Contest relevance: proves a new-project boundary and avoids pre-existing-work claims.

## 2026-08-17 - Deterministic governance domain

- Commit: `5d28337` (`feat: add deterministic governance domain`).
- Goal: encode hard governance rules outside the model.
- Result: typed change requests, capabilities, authority grants, permits, policies, evidence,
  validation results, human-decision packages, and governance decisions; deterministic evaluator
  and path-safety primitives implemented.
- Tests: 21 tests passed; Ruff lint and format checks passed; bytecode compilation passed; project
  doctor and strict factory baseline passed.
- Important decision: the model may gather and interpret context, but cannot override permit,
  authority, scope, evidence, or validator gates.
- Contest relevance: establishes the non-ornamental control plane that the Strands agent will use.

## 2026-08-17 - Synthetic end-to-end governance workflow

- Commit: `b5e0460` (`feat: add synthetic governance workflow`).
- Goal: complete the real-work workflow against a public, self-contained software factory.
- Result: read-only `GovernanceSource` contract, synthetic adapter, two fixed approved validators,
  append-only digest-bearing audit records, human and JSON CLI output, stable exit codes, and safe,
  deny, and escalation demos implemented.
- Tests: 32 tests passed across unit, contract, integration, security, and scenario suites; Ruff,
  compilation, project doctor, and strict factory baseline passed; `governor --verbose demo all`
  produced the three expected outcomes.
- Important decision: objective denials stop before validator execution; only allowlisted validator
  kinds run and raw output is excluded from logs.
- Contest relevance: demonstrates real end-to-end governance work, autonomy for safe changes,
  deterministic rejection, and a human escalation package. Strands orchestration remains pending.

## 2026-08-17 - Strands Governor agent loop

- Commit: `ca1559a` (`feat: add Strands governor agent`).
- Goal: make Strands central and non-ornamental without granting the model governance authority.
- Result: one Strands `Agent`, three purpose-built custom tools, current structured-output API,
  typed tool hooks, deterministic offline model double, verified agent/domain consistency, Bedrock
  provider boundary, and `agent-demo` CLI implemented.
- Tests: 39 tests passed; all three agent scenarios completed the four-step Strands trace; prompt
  injection in an untrusted objective did not change authority; a contradictory model report was
  rejected; Bedrock cost acknowledgement was enforced; all static and baseline checks passed.
- Important decision: offline mode demonstrates orchestration reproducibly but is not represented as
  production intelligence. Bedrock remains uncalled and unproven until human authorization.
- Contest relevance: Strands now performs the actual inspection/evaluation tool loop and produces
  schema-validated output while hard governance remains deterministic.

## 2026-08-17 - Agent evaluations and audit integrity

- Commit: `f76751f` (`feat: add agent evaluations and audit verification`).
- Goal: make behavior and persisted evidence independently inspectable.
- Result: versioned four-case evaluation suite, ten aggregate safe-autonomy metrics, append-only
  evaluation reports, canonical audit digest verification, tamper and symlink rejection, accurate
  automatic-action records, and safe debug output implemented.
- Tests: 45 tests passed; evaluation baseline 4/4; decision/tool/policy/evidence metrics 1.000;
  false allow, false deny, hallucinated policy, and unnecessary interruption rates 0.000; tampered
  audit record rejected.
- Important decision: offline evaluation results are explicitly fixture-scoped and do not claim
  Bedrock production performance.
- Contest relevance: provides repeatable evidence for technical implementation, safe autonomy, and
  presentation without hiding model or fixture limitations.

## 2026-08-17 - Privacy-preserving real-factory inventory

- Commit: `99ff87d` (`feat: add read-only factory inventory adapter`).
- Goal: prove post-contest utility without coupling Governor to private paths or fabricated schemas.
- Result: fixed-path, non-recursive, read-only GoNucleo inventory adapter and CLI implemented; actual
  factory inspected using aggregate output only; project identifiers and absolute paths excluded.
- Tests: 49 tests passed before final documentation gate; actual inspection confirmed catalog and
  tooling availability while full governance readiness remained false.
- Important decision: no hypothetical registry filenames and no full `GovernanceSource` claim. The
  missing capability, policy, authority, and persistent permit contracts have undefined locations.
- Contest relevance: demonstrates a credible path to real adoption while preserving the public and
  private boundary.

## 2026-08-17 - Clean-clone and submission-draft gate

- Commit: `ed1c142` (`docs: add contest readiness and submission drafts`).
- Goal: prove standalone judging access and prepare accurate submission materials.
- Result: a no-hardlink local clone under `/tmp` recreated the Python 3.12 environment from
  `uv.lock`, passed 49 tests, ran safe/deny/escalate through Strands, and produced the 4/4
  evaluation baseline. Testing-access, video, Devpost, security, readiness, journal, and regression
  documents drafted.
- Important decision: the failed shared Regression Guard wrapper is disclosed separately; direct
  critical validation passed, but the incompatible wrapper is not relabeled as a pass.
- Contest relevance: provides the reproducibility and presentation foundation required for judging.

## 2026-08-17 - AgentCore report-only evaluation

- Commit: `6a034d7` (`docs: evaluate AgentCore deployment path`).
- Goal: determine whether cloud hosting materially improves the submission before adding AWS
  dependencies or resources.
- Result: official Runtime, direct-deploy, observability, and pricing documentation reviewed;
  minimal CodeZip architecture, cost illustration, USD 5 proposed ceiling, lifecycle, cleanup, and
  human gates documented.
- Decision: defer implementation and deployment until an authorized Bedrock model evaluation,
  credentials, budget, and explicit spend approval exist.
- Contest relevance: preserves an AWS enhancement path without weakening the working local MVP or
  creating uncontrolled cost.

## 2026-08-17 - Audited validator failure recovery

- Commit: `546f963` (`fix: audit required validator failures`).
- Goal: fail closed without losing evidence when approved validation cannot complete.
- Result: a missing required validator definition becomes a typed `ERROR`; failed project tests
  withhold raw output; both produce `VALIDATION_FAILED` and a verifiable audit record. Missing
  evidence remains `INCOMPLETE_EVIDENCE` after passing tests.
- Tests: 52 passed, including three new integration recovery cases; full static, compilation,
  doctor, and factory baseline passed.
- Contest relevance: demonstrates that Governor handles operational failure as governed work rather
  than crashing or silently allowing the change.

## 2026-08-17 - Reproducible public CI

- Commit: `601b633` (`ci: add reproducible validation workflow`).
- Goal: make the same standalone quality gate executable by judges and contributors on every push
  and pull request.
- Result: read-only GitHub Actions workflow added with third-party actions pinned by commit digest,
  locked uv/Ruff dependencies, and Python 3.11/3.12 coverage. The project validation script now
  owns static checks rather than relying on a host-global Ruff installation.
- Tests: 52 passed under Python 3.11.15 and 3.12.13; both runs passed Ruff check, formatting, doctor,
  and the private factory baseline. Strands safe/deny/escalate and the 4/4 evaluation baseline also
  passed locally. A hosted run remains impossible until publication is authorized.
- Important decision: CI has read-only repository permission and performs no Bedrock call,
  deployment, release, commit, or push.
- Contest relevance: judges receive a visible, repeatable quality gate without credentials or paid
  inference.

## 2026-08-17 - Post-commit clean-clone verification

- Commit: `3df1a8f` (`docs: record clean-clone ci evidence`).
- Goal: verify the versioned CI increment outside the development worktree.
- Result: a no-hardlink clone of `601b633` installed the exact lock and passed the standalone gate
  under CPython 3.11.15 and 3.12.13. The Python 3.11 run also produced the expected ALLOW, DENY, and
  ESCALATE outcomes through Strands and passed the versioned evaluation 4/4. The tracked clone
  remained clean after all commands.
- Tests: 52/52 on each Python version; Ruff check and formatting pass; agent decision, tool
  selection, policy grounding, and evidence metrics 1.000; relevant false rates 0.000.
- Limitation: this is local CI-equivalent evidence. A GitHub-hosted run is impossible before the
  repository publication gate is authorized.

## 2026-08-17 - Publication boundary audit

- Commit: `8d00ff4` (`docs: audit public repository boundary`).
- Goal: reduce public-repository privacy, provenance, dependency-license, and supply-chain risk
  without publishing or changing a remote.
- Result: current files and independent history scanned with no personal-path, common-secret,
  deleted-file, binary, or oversized-artifact finding. The expected `.env.example` contains no
  values. Locked package metadata is compatible with normal Apache-2.0 distribution; no dependency
  source is vendored. Public-facing script messages were converted to English.
- Tests: strict factory validation initially caught that seven Spanish README labels are normative
  Golden Path inputs. Those labels were restored, the exception was documented, and the full gate
  was rerun rather than weakening the private factory contract.
- Human gate: antecedent names, private commit identifiers, GoNucleo owner disclosure, Apache-2.0
  acceptance, and actual publication still require explicit approval.
- Contest relevance: protects the public/private boundary and makes the provenance disclosure
  defensible without pretending an automated scan is legal or privacy authorization.

## 2026-08-17 - Private Codex advisory intelligence boundary

- Commit: pending explicit human authorization.
- Goal: remove Bedrock as a mandatory source of useful private-runtime intelligence while keeping
  deterministic governance authoritative and Strands central.
- Official research: current OpenAI Codex CLI, `codex exec`, `codex mcp-server`, app-server, ChatGPT
  authentication, and configuration documentation; current Strands MCP, custom model provider, and
  provider documentation.
- Spike result: Codex MCP returned useful risk content in events but did not produce a consumable
  final tool result through the locked Strands/MCP versions. Stable `codex exec` returned a
  schema-valid evidence-backed report and was selected. Three opt-in subscription-backed spike
  invocations completed through the explicitly selected private ChatGPT profile; no API-key billing,
  Bedrock, AWS resource, repository mutation, or publication occurred.
- Implementation: typed advisory request/report/envelope, low-coupling provider protocol,
  least-privilege Codex subprocess adapter, request-bound Strands tool, fixed synthetic CLI spike,
  fake unit tests, and opt-in local integration test.
- Security: Governor never reads or copies the authentication file; the command forces ChatGPT
  login, ignores private config/rules, disables shell/web/image/subagent tools, runs read-only and
  ephemeral in a temporary directory, filters environment variables, validates bounded structured
  output, and suppresses raw provider errors.
- Regression fix: the three existing governance tools are now async and explicitly sequential. This
  avoids a reproducible Strands 1.52 synchronous thread-dispatch stall while preserving their
  mandatory order; a regression test protects the execution strategy.
- Tests: the offline gate passed 61 tests in 0.824 seconds: 60 passed and the authenticated Codex
  integration was skipped as designed. The separately authorized local integration passed 1/1 in
  8.261 seconds using only the fixed synthetic request. Factory baseline, Ruff, formatting, and
  project doctor all passed.
- Decision: private runtime uses Codex as a subordinate specialized capability, not as a custom
  Strands model provider. Bedrock remains optional for a future judge-accessible contest runtime and
  was not activated.

## 2026-08-17 - Sanitized Evidence Boundary and first real observation

- Commits: `e3827b7` typed evidence/privacy contracts; `474fbe6` sanitized-only intelligence
  enforcement; `4446aa0` read-only real-factory evidence adapter; `dfb8e83` adversarial privacy
  scenarios; `3ed74b1` privacy model, ADR, source map, and readiness documentation.
- Goal: consume useful real factory evidence without granting Governor, Strands, or Codex broad
  repository access and without turning privacy into a prompt convention.
- Contracts: separate local `RawEvidence` and external-safe `SanitizedEvidence`; explicit
  PUBLIC/INTERNAL/CONFIDENTIAL/SECRET classes; fact/inference/policy/human/model kinds; source role,
  trust, provenance, logical paths, aliases, redactions, digests, and deterministic external policy.
- Security: fixed-source adapter, no application recursion or tool execution, path confinement,
  symlink rejection, code/free-text minimization, critical secret patterns, SECRET hard block,
  normative-source validation, provider pre-start type enforcement, and audit records without raw
  values.
- Real case: a read-only governance-readiness observation ran against the private factory. Only
  sanitized aggregate source states were produced; no project identifiers, source content, private
  absolute paths, credentials, or logs entered Governor artifacts. The factory Git status was
  identical before and after the run.
- Governor result: `INCOMPLETE_EVIDENCE`, with no authoritative change decision, because required
  capability, authority, and permit registries are absent and several normative sources remain
  partial. No default was invented.
- Codex result: one opt-in network-enabled invocation through the explicitly selected ChatGPT
  profile received only the sanitized object and returned evidence-backed architectural risks under
  `ADVISORY_ONLY`. Two earlier sandboxed attempts failed before inference because network was
  unavailable; raw stderr remained suppressed.
- Tests: the final offline gate passed 84 tests in 0.846 seconds: 83 passed and the authenticated
  Codex integration was skipped as designed. Factory baseline, Ruff, formatting, project doctor,
  and all original 52 tests passed.
- External services: no Bedrock, AWS credentials, API-key billing, AgentCore, deployment,
  publication, or push. One successful call consumed local ChatGPT/Codex quota.
- Closure tooling limitation: the generic runtime-reality wrapper resolved the parent monorepo even
  though Governor has no deployed runtime change and refreshed one ignored frontend build directory
  outside Governor. No new tracked factory diff was detected. Cleanup was deliberately not attempted
  because deleting a pre-existing ignored artifact would be destructive and outside this permit.

## 2026-08-20 - Versioned synthetic authority registry

- Goal: make the public demo's actor authority source explicit and schema-versioned without
  modifying or inferring anything from the private factory.
- Implementation: `AuthorityRegistry` wraps `AuthorityGrant` records under
  `governor.authority-registry.v1`; duplicate actors are rejected before the read-only synthetic
  adapter resolves an authority. The fixture and contract tests cover the valid and duplicate cases.
- Boundary: the real-factory inventory remains fail-closed and continues to declare the missing
  real authority registry. No private source, path, content, credential, or factory file was read
  or changed for this increment.

## 2026-08-20 - Explicit authority-registry schema gate

- Goal: prevent an omitted schema version from being silently accepted as the current authority
  contract.
- Implementation: `schema_version` is required, not defaulted. The domain and adapter tests reject
  legacy lists, missing or unknown versions, unexpected fields, and duplicate actors.
- Boundary: the hardening applies only to the public synthetic contract; it neither reads nor
  changes the private factory.

## 2026-08-20 - Versioned synthetic capability registry

- Goal: give the public demo's capability source the same explicit, fail-closed contract as its
  authority source.
- Implementation: `CapabilityRegistry` requires `governor.capability-registry.v1` and unique
  capability IDs before the read-only adapter resolves a capability. Legacy and missing-version
  inputs are covered by focused tests, including failure-recovery compatibility.
- Boundary: the private factory still has no machine-readable capability registry and remains
  intentionally incomplete for real governance evaluation.

## 2026-08-20 - Versioned synthetic permit registry

- Goal: make the demo's request-specific authority source explicit without turning absent permits
  into malformed configuration.
- Implementation: `PermitRegistry` requires `governor.permit-registry.v1`, rejects duplicate permit
  and request IDs, and permits an empty collection so absence resolves deterministically to DENY.
- Boundary: no private Change Permit tool output or factory source was parsed, copied, or changed.

## 2026-08-20 - Versioned synthetic policy registry

- Goal: prevent the public demo from silently evaluating a request with an absent policy source.
- Implementation: `PolicyRegistry` requires `governor.policy-registry.v1`, at least one policy, and
  unique policy IDs before policies can enter deterministic evaluation.
- Boundary: the private factory policy registry is still absent; no private policy prose was parsed
  or treated as authoritative.

## 2026-08-20 - Versioned synthetic validator registry

- Goal: make approved validator definitions explicit while preserving the existing fail-closed
  recovery path for an unavailable required validator.
- Implementation: `ValidatorRegistry` requires `governor.validator-registry.v1` and unique IDs;
  missing required definitions still become audited validation errors.
- Boundary: no private validator declarations or executable tooling was consumed.

## 2026-08-20 - Governance-bundle contract suite

- Goal: prove that every normative synthetic registry is loaded before Governor may issue a
  deterministic decision.
- Implementation: a transversal workflow contract starts from the valid bundle and then corrupts
  each registry in isolation. Every corrupt source fails before a decision or audit record exists.
- Boundary: all inputs are copied from public synthetic fixtures into temporary directories.
