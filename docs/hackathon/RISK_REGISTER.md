# Risk Register

Last reviewed: 2026-08-17

| ID | Risk | Likelihood | Impact | Mitigation and gate | Status |
|---|---|---|---|---|---|
| R-01 | Pre-existing work lacks disclosure | Medium | Critical | New repository, synthetic fixtures, Git-first provenance, no Living Memory code | Controlled |
| R-02 | Private factory material reaches public Git | Medium | Critical | Private-by-default boundary, synthetic fixtures, local publication audit | Automated scan passed; human disclosure review open |
| R-03 | LLM becomes governance authority | Medium | Critical | Deterministic policy, permit, authority and evidence gates | Architecture control |
| R-04 | Prompt injection changes agent behavior | High | High | Treat content as data, narrow tools, adversarial tests | Controlled in core suite; Bedrock eval pending |
| R-05 | Path traversal or symlink escapes scope | Medium | Critical | Resolve and confine paths; test escapes | Controlled for implemented adapters/tools |
| R-06 | Missing evidence causes false ALLOW | Medium | Critical | Deny by default, typed evidence, schema validation | Controlled by deterministic tests |
| R-19 | Missing validator crashes without audit evidence | Medium | High | Typed validator-unavailable result and integration recovery tests | Controlled |
| R-07 | Governor escalates every case | Medium | High | Safe scenario must close automatically; measure interruptions | Demo gate |
| R-08 | Strands is ornamental | Medium | Critical | Real Agent, custom tools, structured output and observable loop | Controlled |
| R-09 | Paid model calls make tests flaky | High | High | Deterministic model double and opt-in integration tests | Controlled |
| R-10 | AWS creates uncontrolled cost | Low now | High | No cloud before estimate, budget and approval | Blocked |
| R-11 | Host Python dependency incompatibility | Medium | Medium | Isolated environments, project floor 3.11, lock, Python 3.11/3.12 clean-clone gates | Controlled |
| R-12 | Strands API changes | Medium | Medium | Pin 1.52.0 and use current APIs | Controlled |
| R-13 | Dirty parent contaminates commits | Medium | High | Independent Git; never stage parent | Controlled |
| R-14 | Capability proposal is mistaken for registry | Medium | High | Synthetic adapter first; real adapter fails closed | Controlled |
| R-15 | Demo is not reproducible | Medium | High | Scenario tests, one-command demo, clean-clone rehearsal | Controlled locally; public URL pending |
| R-16 | Public testing needs private credentials | Medium | High | Free local synthetic path with no credentials | Architecture control |
| R-17 | License or ownership blocks publication | Low for new code | Critical | Apache-2.0, no vendored work, dependency metadata audit, final human IP review | Engineering audit passed; human acceptance open |
| R-18 | Inference is presented as fact | Medium | High | Typed evidence kinds and exact model/domain consistency check | Controlled for MVP |
| R-20 | Private evidence is over-shared with Codex | Medium | Critical | Fixed typed request, synthetic spike, no repository access, evidence minimization, explicit future privacy gate | Controlled for spike; real-factory contract blocked |
| R-21 | Codex CLI behavior or flags drift | Medium | High | Record tested version, strict config, fake command-contract tests, opt-in local compatibility test | Controlled for current version |
| R-22 | Codex MCP notifications do not interoperate with the locked Strands/MCP client | Medium | Medium | Keep MCP deferred and use stable `codex exec`; require passing compatibility matrix before adoption | Open and non-blocking |
| R-23 | Private Codex quota or service availability interrupts Governor intelligence | Medium | Medium | Advisory-only fail-closed provider, explicit quota acknowledgement, deterministic governance remains offline-capable | Controlled by separation |

## Stop conditions

Stop and request human action before changing authentication, selecting a new private evidence
contract, AWS spend, public publication, irreversible deletion, exposure of private material, or a
product-direction change that abandons governance for AI-assisted software factories.
