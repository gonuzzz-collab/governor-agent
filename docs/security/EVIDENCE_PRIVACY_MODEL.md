# Evidence Privacy Model

Status: implemented for the read-only factory observation boundary.

## Security objective

Governor should receive the minimum evidence needed for a useful governance result. External
intelligence should receive an even narrower, explicitly permitted representation. Privacy must
remain enforced when repository content requests more access or attempts prompt injection.

## Threat model

The boundary addresses:

- accidental inclusion of unrelated private files or complete repositories;
- proprietary code and strategic architecture leaving the machine;
- personal absolute paths, usernames, mount names, and workspace identifiers;
- credentials, tokens, private keys, auth files, environment files, and obvious passwords;
- private project, component, customer, product, or person identifiers;
- repository prompt injection attempting to bypass sanitization;
- descriptive documents being misclassified as normative policy;
- raw values leaking through audit logs or provider errors;
- a model attempting to emit governance authority.

It does not claim complete DLP, legal anonymization, or detection of every encoded or novel secret.

## Data flow

```text
RAW FACTORY DATA
  -> fixed local extraction
  -> RawEvidence
  -> classification and secret detection
  -> minimization
  -> path and identifier sanitization
  -> SanitizedEvidence
  -> deterministic ExternalIntelligencePolicy
  -> Governor
  -> optional Codex advisory analysis
```

The raw object is local only. Codex has no repository path, file handle, shell scope, or mechanism
to request more evidence.

## Classification

### PUBLIC

Content deliberately suitable for external release. External processing is allowed when useful,
but personal paths are still removed.

### INTERNAL

Private operational information of low sensitivity. It is eligible only after minimization,
logical path conversion, and identifier aliasing. Free-form repository text and code are removed.

### CONFIDENTIAL

Proprietary or strategically sensitive information. Only structural metadata such as bounded
counts, booleans, enumerated states, and approved hashes may remain. Code, free text, paths, and
identifiers are removed or transformed.

### SECRET

Credentials, authentication material, private keys, sensitive personal data, or explicitly secret
content. The policy returns `BLOCK_EXTERNAL_EXPOSURE`. Statements and secret-derived hashes are not
included in the external representation.

## Evidence contract

`RawEvidence` records local source type, explicit classification, evidence kind, trust, source role,
local identifiers, event/change type, a confined source path, bounded facts, policy references, and
timestamp. Raw fact values are masked in normal representations.

`SanitizedEvidence` records:

- a non-authority-bearing evidence ID;
- effective classification;
- stable project and component aliases;
- event and change type;
- typed bounded statements;
- applicable policy references;
- approved content hashes;
- redaction reasons;
- logical provenance and trust;
- external-processing action and permission;
- timestamp.

The sanitized model rejects inconsistent classification/action pairs. Intelligence requests reject
anything that is not an already validated `SanitizedEvidence` instance.

## Minimization rules

Only facts marked necessary are considered. Code is never forwarded. Internal and confidential
free text is removed and may produce a SHA-256 digest only when no secret was detected.
Confidential evidence retains structural metadata only. Secret evidence produces neither statements
nor content-derived hashes.

The real adapter performs an earlier semantic extraction step: it converts fixed TOML contracts and
source readiness into aggregate counts and enumerated states. It does not place source documents in
`RawEvidence`.

## Path privacy

Allowed relative resources use logical schemes such as `factory://` and `project://`. Personal
absolute path prefixes, Windows user paths, configured private identifiers, and the local workspace
name are removed. Evidence source paths must resolve inside the configured factory root and must be
regular non-symlink files.

## Identifier privacy

Non-public project and component identifiers become stable aliases such as `PROJECT_<digest>` and
`COMPONENT_<digest>`. This enables correlation across observations without sending the original
name. The aliases are pseudonyms, not cryptographic anonymity; predictable identifiers may be
guessable and must not be treated as secrets.

## Secret handling

The bounded detector checks critical shapes including:

- OpenAI, AWS, and common source-control token forms;
- bearer tokens and obvious credential assignments;
- private-key headers;
- `.env`, auth, credential, SSH, and AWS credential paths.

A match upgrades the effective classification to `SECRET` and blocks external processing. Audit
records retain detector category IDs and `secret_detected=true`, never the matched value. Provider
stderr is not surfaced.

## Trust and authority

Supported trust levels distinguish trusted governance, trusted validators, observed sources,
untrusted repository content, model output, and human confirmation. Source role independently marks
content as `NORMATIVE` or `DESCRIPTIVE`.

Only trusted governance or human-confirmed normative sources can produce `POLICY` evidence. Model
output is always descriptive `MODEL_ADVISORY`; it cannot become policy, a permit, authority, or an
ALLOW/DENY/ESCALATE decision.

## External intelligence policy

| Classification | Deterministic action | Model payload |
|---|---|---|
| `PUBLIC` | `ALLOW` | Minimal public evidence |
| `INTERNAL` | `ALLOW_SANITIZED` | Sanitized and minimized facts |
| `CONFIDENTIAL` | `ALLOW_METADATA_ONLY` | Structural metadata only |
| `SECRET` | `BLOCK_EXTERNAL_EXPOSURE` | None |

The LLM does not participate in this decision.

## Codex boundary

The existing `codex exec` adapter receives an `IntelligenceRequest` containing only
`SanitizedEvidence`. It rejects raw evidence and blocked sanitized evidence before process startup.
The invocation remains ephemeral, read-only, schema-bound, tool-disabled, request-scoped, and
`ADVISORY_ONLY`.

## Audit trail

The append-only evidence audit records:

- raw evidence ID and raw fact names, but not values;
- original and effective classification;
- retained and removed fact names;
- redaction and detector categories;
- deterministic external-processing reason;
- the exact sanitized payload eligible for Codex;
- whether Codex received it;
- the Governor readiness result;
- an integrity digest.

Audit storage must be outside the real factory. Secret values, raw files, local project names, and
absolute paths are not persisted.

## Local-only data

The following remain local and outside committed artifacts:

- real factory root and personal paths;
- raw project identifiers and catalog entries;
- source and documentation contents;
- credentials and Codex authentication files;
- real audit files;
- account configuration and provider stderr.

## First real observation

The implemented case reads the fixed factory manifest, catalog, and known contract entrypoints. It
produces aggregate governance-readiness evidence. The deterministic result is
`INCOMPLETE_EVIDENCE` because mandatory machine-readable governance contracts remain absent or
partial. No change decision is fabricated. The factory Git status was unchanged before and after
the real run.

An opt-in Codex run received only the final sanitized object and returned evidence-backed
architectural risks. Its report remained advisory and did not alter the Governor result.

## Known limitations

- Encoded, fragmented, novel, or context-dependent secrets may evade pattern detection.
- False positives intentionally fail closed and require local human review.
- Stable aliases can support correlation but are not irreversible anonymization.
- Classification and semantic extraction need reviewed adapters for each new source type.
- Current real-factory evidence is aggregate readiness data, not a complete change request.
- Complete real governance remains blocked on typed authority, policy, capability, and permit
  sources.
