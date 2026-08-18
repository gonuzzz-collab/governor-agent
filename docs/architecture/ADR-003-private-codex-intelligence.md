# ADR-003: Use Codex Exec for Private Advisory Intelligence

- Status: accepted for an experimental local vertical slice
- Date: 2026-08-17

## Context

Governor needs useful model intelligence in a private factory without making Amazon Bedrock, AWS
credentials, or a separate OpenAI API key mandatory. The existing deterministic policy, authority,
permit, scope, validator, evidence, and ALLOW/DENY/ESCALATE gates must remain the only governance
authority. Strands must remain the central agent framework.

Only mechanisms documented by OpenAI and Strands were considered:

- OpenAI documents `codex exec` as the stable non-interactive interface, with a read-only default,
  explicit sandbox selection, ephemeral runs, isolated configuration, and JSON Schema output.
- OpenAI documents `codex mcp-server` as a stable stdio server intended for consumption by another
  agent.
- OpenAI marks `codex app-server` experimental and primarily intended for development and
  debugging.
- Strands documents MCP tools through `MCPClient` and custom model providers through the `Model`
  interface.

Official references:

- [Codex developer commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode)
- [Codex MCP server](https://learn.chatgpt.com/docs/mcp-server)
- [Codex app server](https://learn.chatgpt.com/docs/app-server)
- [Codex authentication](https://learn.chatgpt.com/docs/auth)
- [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [Strands MCP tools](https://strandsagents.com/docs/user-guide/concepts/tools/mcp-tools/)
- [Strands custom model providers](https://strandsagents.com/docs/user-guide/concepts/model-providers/custom_model_provider/)
- [Strands model providers](https://strandsagents.com/docs/user-guide/concepts/model-providers/)

## Options evaluated

| Option | Official support | Existing ChatGPT login | Strands role | Security and reproducibility | Coupling | Decision |
|---|---|---|---|---|---|---|
| A. `codex mcp-server` through Strands `MCPClient` | Both sides document the mechanism as supported | Yes, through the selected `CODEX_HOME` | Native MCP tool consumption | Strong tool boundary in principle; local spike exposed an event-validation interoperability problem with the locked versions | Low | Deferred pending a compatible version matrix |
| B. `codex exec` behind a purpose-built Strands tool | Stable documented Codex automation interface | Yes | Strands owns the request-bound tool; Codex is subordinate | Explicit schema, timeout, ephemeral run, disabled tools, read-only sandbox, minimal environment, and no approval path | Low | Chosen |
| C. Strands custom model provider over Codex CLI or app server | Strands custom providers are supported; app server is experimental | Potentially | Codex would impersonate a Strands model | Requires translating messages, tool calls, streaming events, stop reasons, and errors between two agent protocols | High | Rejected for this increment |
| D. Bedrock model provider | Supported by Strands | Not applicable | Native Strands model | Reproducible only with AWS identity, region, model access, and an explicit spend gate | Low inside Strands | Retained as optional contest runtime |

### Spike evidence

The MCP spike used synthetic evidence, a temporary workspace, a read-only sandbox, and no
repository mutation. Codex produced useful risk content in event notifications, but the current
locked Strands/MCP client path rejected Codex-specific notification shapes and returned no usable
final tool content. This is a local compatibility observation, not a claim that the documented MCP
architecture is generally broken.

The `codex exec` spike used the same synthetic, read-only task and returned a schema-valid report
containing evidence-backed architectural risks. It reused the explicitly selected ChatGPT-authenticated
Codex profile and did not require Bedrock or an OpenAI API key.

Observed local compatibility set for the spike:

- Codex CLI 0.147.0
- Strands Agents 1.52.0
- Python MCP package 1.29.0

No private profile path, token, authentication file, raw event log, or account metadata belongs in
the repository.

## Decision

Use `codex exec` as the first private advisory intelligence adapter. Governor binds a typed,
minimal `IntelligenceRequest` to a no-argument Strands custom tool. Codex receives only the fixed
objective, scope, and evidence selected by Governor. Its output is a typed architectural-risk
report with no governance-decision field. Governor adds the `ADVISORY_ONLY` authority label itself.

This slice is experimental and deliberately separate from the authoritative evaluation workflow.
It proves the provider boundary and a safe invocation contract before any deeper integration.

## Runtime compositions

### PRIVATE FACTORY RUNTIME

```text
Governor Core
  |-- deterministic governance (sole ALLOW/DENY/ESCALATE authority)
  |-- purpose-built tools
  `-- intelligence boundary
        `-- Strands request-bound tool
              `-- codex exec
                    `-- explicitly selected ChatGPT-authenticated CODEX_HOME
```

The private path sends sanitized structured evidence, not a repository path. It needs the Codex
service network connection and consumes the selected ChatGPT plan quota, but it needs neither an
OpenAI API key nor AWS.

### PUBLIC HACKATHON RUNTIME

```text
Governor Core
  |-- deterministic governance (sole ALLOW/DENY/ESCALATE authority)
  `-- Strands Agent
        `-- optional Amazon Bedrock model
              `-- judge-accessible AWS configuration and explicit spend acknowledgement
```

The existing offline deterministic model remains the default for tests, free judging access, and
clean-clone demonstrations. Bedrock is not activated by this decision.

## Invocation contract

Governor, not Codex, fixes the input and execution policy:

- an explicit, absolute, existing `CODEX_HOME` is mandatory;
- ChatGPT is forced as the login method and `OPENAI_API_KEY` is not forwarded;
- user config and user/project exec-policy rules are not loaded;
- approval policy is `never` and filesystem sandbox mode is `read-only`;
- shell, web search, image inspection, and subagent tools are disabled;
- the working directory contains only the temporary output schema;
- session rollout persistence is disabled;
- the child environment is allowlisted;
- output is schema-validated and bounded, with a bounded timeout;
- raw stderr and local paths are not surfaced in provider errors.

Governor does not read, copy, parse, log, or fixture any credential file. Codex CLI itself accesses
the credentials in the selected profile as part of its documented authentication flow.

## Authority boundary

Codex may identify and explain risks supported by supplied evidence. It cannot:

- create or reinterpret policy;
- grant authority or expand a permit;
- add files or evidence to scope;
- run validators or mutate a repository;
- emit an authoritative ALLOW, DENY, or ESCALATE;
- override a deterministic Governor decision.

Any output that violates the schema, including a governance `status` field, fails closed.

## Consequences

Benefits:

- private Governor intelligence can reuse an existing ChatGPT-authenticated Codex CLI;
- no Bedrock, AWS credential, or additional OpenAI API key is required;
- Strands remains the framework boundary through a purpose-built custom tool;
- the adapter is local, opt-in, structured, and replaceable;
- Bedrock remains available without coupling private runtime to AWS.

Costs and residual risks:

- Codex CLI flags and event behavior can change; the tested compatibility set must be maintained;
- the run depends on Codex service availability and consumes the selected account quota;
- supplied evidence leaves the machine for model processing and therefore must be minimized and
  free of secrets or private raw content;
- direct MCP adoption remains blocked until the notification/result path passes an opt-in
  compatibility test;
- this vertical slice does not yet inject Codex into authoritative evaluation or let it inspect a
  real factory.

## Revisit conditions

Reconsider MCP after a locked Codex/Strands/MCP combination returns a schema-valid final result
without notification-validation errors. Reconsider a custom model provider only if Governor needs
Codex to implement the complete Strands `Model` contract and app-server reaches a suitable stable
maturity. Promote the spike into a normal private-factory workflow only after a human approves the
exact evidence-selection and privacy policy.
