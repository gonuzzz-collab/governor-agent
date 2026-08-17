# Human Actions

Last reviewed: 2026-08-17

These tasks require identity, money, publication authority, or a personal eligibility decision.
They do not block the local MVP unless stated.

| Priority | Action | Deadline or gate | Current evidence | Why human |
|---|---|---|---|---|
| High | Confirm Devpost registration and personal eligibility | Before submission | Not verified | Legal identity and residency |
| High | Request USD 50 AWS Promotional Credits | 2026-09-11 12:00 PT | Not verified | Account form and terms |
| High | Create or confirm AWS Builder ID | Required for submission | Not verified | Personal account |
| Medium | Create or confirm AWS account and least-privilege credentials | Before Bedrock testing | AWS CLI absent | Authentication and billing |
| Medium | Approve AWS budget and cost ceiling | Before paid call or deployment | No budget observed | Money and risk |
| Medium | Choose Bedrock model and region for the first live evaluation | After credentials and budget | Provider boundary only | Model access, regional availability, and cost |
| High | Approve antecedent and owner identifiers for public disclosure | Before publication | Automated audit passed; PUBLICATION_AUDIT.md lists exact gate | Privacy and ownership |
| High | Approve public repository creation and push | After privacy and license review | Local only; no remote changed | Publication |
| High | Approve public YouTube or Vimeo video | Before submission | Not created | Publication rights |
| High | Approve Devpost submission | By 2026-09-14 17:00 PT | Not created | Binding entry |
| Medium | Decide whether to deploy AgentCore | After local MVP and estimate | Deferred | Spend and cloud footprint |
| Medium | Review final provenance and Apache-2.0 IP disclosure | Before publication | Engineering license review passed; human acceptance pending | Ownership |
| Low | Decide whether to publish builder.aws posts | Optional bonus | Journal reserved only | Public authorship |

## AWS cost controls to establish

- Promotional credit receipt and expiration.
- Billing alerts or budget.
- Region and model access.
- Maximum permitted development spend.
- Runtime idle and maximum lifetime if AgentCore is approved.
- Cleanup plan and proof after deployment.

The current report-only recommendation is a maximum USD 5 first-experiment ceiling, no more than
20 invocations, one runtime/endpoint, short session limits, and same-session teardown. This proposal
does not authorize spend.

No code will assume that a ChatGPT or Codex subscription includes AWS or model API credits.
