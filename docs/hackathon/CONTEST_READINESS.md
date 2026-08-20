# Contest Readiness

Last reviewed: 2026-08-17

| Gate | Status | Evidence or blocker |
|---|---|---|
| New-project provenance | PASS | Independent history and PROVENANCE.md |
| Local MVP | PASS | Real Strands tool loop and end-to-end workflow |
| Deterministic governance | PASS | Domain and scenario suites |
| Safety | PASS WITH RISK | Security tests; Bedrock behavior not evaluated |
| Reproducibility | PASS | Commit `4248f08` clean clone; locked gate, 103 tests, Strands demo, and 9/9 eval |
| Public CI definition | PASS LOCALLY / NOT HOSTED | SHA-pinned read-only workflow; Python 3.11/3.12 clean-clone gates pass; GitHub run requires publication |
| Public synthetic demo | PASS | Safe, deny, escalate |
| Apache-2.0 license | PASS | Top-level LICENSE |
| English README | PASS | Public instructions and boundaries |
| Architecture diagram | PASS | Mermaid diagram in docs/architecture |
| Agent evaluations | PASS | 9-case offline baseline; 9/9, false allow/deny 0.000 |
| Sanitized private evidence boundary | PASS WITH LIMITS | Typed classification, deterministic policy, secret/path controls, audit, and read-only real observation; complete governance registries remain pending |
| Provenance disclosure | PASS FOR LOCAL | Final human/IP review pending |
| Security review | PASS WITH OPEN CLOUD ITEMS | No cloud call or deployment tested |
| Publication privacy scan | PASS WITH HUMAN GATE | No secret/path/binary finding; antecedent and owner disclosures need approval |
| Testing access | DRAFT | Public clone URL pending publication |
| Five-minute video plan | DRAFT | Recording and public upload pending |
| Devpost copy | DRAFT | Human review and submission pending |
| Public repository | BLOCKED ON HUMAN | Publication authorization required |
| AWS Builder ID | BLOCKED ON HUMAN | Account identity required |
| AWS credits/budget | BLOCKED ON HUMAN | Terms, billing, and cost decision required |
| Bedrock integration test | NOT RUN | Credentials and spend authorization required |
| AgentCore | DEFERRED AFTER ASSESSMENT | Potential value; Bedrock eval, credentials, USD 5 ceiling, and human approval required |

Governor is an implemented local MVP, not yet a contest-ready public submission. Human-owned
identity, publication, cloud-cost, and final IP gates remain intentionally unresolved.
