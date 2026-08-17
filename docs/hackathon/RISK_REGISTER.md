# Risk Register

Last reviewed: 2026-08-17

| ID | Risk | Likelihood | Impact | Mitigation and gate | Status |
|---|---|---|---|---|---|
| R-01 | Pre-existing work lacks disclosure | Medium | Critical | New repository, synthetic fixtures, Git-first provenance, no Living Memory code | Controlled |
| R-02 | Private factory material reaches public Git | Medium | Critical | Private-by-default boundary, no real fixtures, secret scan | Open until publication |
| R-03 | LLM becomes governance authority | Medium | Critical | Deterministic policy, permit, authority and evidence gates | Architecture control |
| R-04 | Prompt injection changes agent behavior | High | High | Treat content as data, narrow tools, adversarial tests | Planned |
| R-05 | Path traversal or symlink escapes scope | Medium | Critical | Resolve and confine paths; test escapes | Planned |
| R-06 | Missing evidence causes false ALLOW | Medium | Critical | Deny by default, typed evidence, schema validation | Planned |
| R-07 | Governor escalates every case | Medium | High | Safe scenario must close automatically; measure interruptions | Demo gate |
| R-08 | Strands is ornamental | Medium | Critical | Real Agent, custom tools, structured output and observable loop | Phase 4 gate |
| R-09 | Paid model calls make tests flaky | High | High | Deterministic model double and opt-in integration tests | Controlled |
| R-10 | AWS creates uncontrolled cost | Low now | High | No cloud before estimate, budget and approval | Blocked |
| R-11 | Python 3.14 dependency incompatibility | Medium | Medium | Upstream floor, lock, environment tests | Open |
| R-12 | Strands API changes | Medium | Medium | Pin 1.52.0 and use current APIs | Controlled |
| R-13 | Dirty parent contaminates commits | Medium | High | Independent Git; never stage parent | Controlled |
| R-14 | Capability proposal is mistaken for registry | Medium | High | Synthetic adapter first; real adapter fails closed | Controlled |
| R-15 | Demo is not reproducible | Medium | High | Scenario tests, one-command demo, clean-clone rehearsal | Contest gate |
| R-16 | Public testing needs private credentials | Medium | High | Free local synthetic path with no credentials | Architecture control |
| R-17 | License or ownership blocks publication | Low for new code | Critical | Apache-2.0, no proprietary reuse, final IP review | Open |
| R-18 | Inference is presented as fact | Medium | High | Typed evidence kinds and explicit explanations | Planned |

## Stop conditions

Stop and request human action before authentication, AWS spend, public publication, irreversible
deletion, exposure of private material, or a product-direction change that abandons governance for
AI-assisted software factories.
