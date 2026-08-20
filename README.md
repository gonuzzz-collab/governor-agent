# Governor Agent

**Governance for AI-assisted software changes: allow, block, or escalate with explicit evidence.**

[Leer en español](README.es.md)

Governor Agent is a new open-source project being built for the **Agents for Humans Hackathon** in the **Professional Agents** track.

Its purpose is simple:

> **Before an AI-assisted software change is accepted, can an agent verify whether the change is authorized, supported by evidence, and safe to proceed — or whether a human decision is required?**

Governor Agent is being implemented as an independent project with the **Strands Agents SDK**. It does not contain proprietary implementation from GoNucleo, Living Memory, or Lexidiam.

---

## Problem

AI coding agents can modify software faster than humans can review every action in detail.

The difficult part is no longer only generating code. It is deciding whether a proposed change should be allowed to proceed.

A useful governance layer needs to answer questions such as:

- Is this actor authorized to make this kind of change?
- Is the target within the permitted scope?
- Does an explicit policy prohibit the action?
- Is required validation evidence available?
- Is the situation clear enough to decide automatically?
- Should the decision be escalated to a person?

Governor Agent explores that layer.

---

## MVP decision model

The hackathon MVP focuses on three outcomes:

```text
Proposed software change
          ↓
     Governor Agent
          ↓
  Policy + authority + scope
          ↓
   Validation evidence
          ↓
 ┌────────┼───────────┐
 ↓        ↓           ↓
ALLOW    BLOCK     ESCALATE
 ↓        ↓           ↓
      Decision record
```

### ALLOW
The proposal is explicitly within scope and required evidence is present.

### BLOCK
The proposal clearly violates an explicit rule or authority boundary.

### ESCALATE
The proposal cannot be decided safely from the available policy and evidence, so human judgment is required.

---

## Hackathon demo scenarios

The first working version will demonstrate three synthetic cases:

1. **Allowed change** — a low-risk modification that is within declared authority and passes required checks.
2. **Blocked change** — a proposal that violates an explicit policy or attempts to modify a protected target.
3. **Escalated change** — an ambiguous or high-impact proposal that requires human approval.

The goal is a complete, understandable end-to-end demonstration rather than a large policy platform.

---

## Design principles

- **Explicit policy over hidden assumptions**
- **Evidence before authorization**
- **Least authority**
- **Fail closed on clear violations**
- **Escalate ambiguity instead of inventing permission**
- **Human responsibility for judgment-heavy decisions**
- **Auditable decision records**

---

## Planned architecture

```text
Change proposal
      ↓
Strands Governor Agent
      ↓
Policy evaluator
      ↓
Authority + scope checks
      ↓
Evidence evaluator
      ↓
Decision engine
      ↓
ALLOW / BLOCK / ESCALATE
      ↓
Human-readable decision record
```

See [`docs/architecture.md`](docs/architecture.md) for the current conceptual architecture.

---

## Repository status

**Status:** initial public scaffold / implementation starting  
**Hackathon:** Agents for Humans Hackathon  
**Track:** Professional Agents  
**Agent framework:** Strands Agents SDK  
**License:** Apache License 2.0

This README deliberately distinguishes planned behavior from implemented behavior. Features will only be described as working after they are implemented and verified.

---

## Scope boundary

Governor Agent is a new and independent implementation created for the hackathon.

It may be informed by broader research and experience with governance, traceability, evidence, and AI-assisted software systems, but this repository does **not** expose proprietary internals from:

- GoNucleo's private software factory;
- Living Memory's proprietary implementation;
- Lexidiam's proprietary implementation;
- private policies, contracts, schemas, infrastructure, or operational documentation.

---

## Authorship, license, and project identity

Governor Agent was originally created by **Patricio Castillo** for the **Agents for Humans Hackathon 2026**.

Copyright © 2026 Patricio Castillo.

The software in this repository is licensed under the **Apache License, Version 2.0**. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).

The Apache License applies to the software distributed in this repository. It does not grant rights to use trade names, trademarks, service marks, or product names except as required for reasonable attribution and description of the origin of the work.

Future proprietary GoNucleo systems, private policies, integrations, and implementations are outside the scope of this repository and are not licensed by its open-source license.

---

## Author

**Patricio Castillo**  
Architecture and governance of AI-assisted systems · Agents · Data sovereignty · Living documentation

Created and maintained by **Patricio Castillo**.  
Developed under **GoNucleo IA**, an independent technology lab.

[Professional portfolio](https://github.com/gonuzzz-collab/mi-portafolio)
