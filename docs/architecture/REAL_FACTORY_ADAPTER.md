# Real Factory Adapter Boundary

Status: aggregate read-only inventory implemented; full governance source intentionally blocked.

`GoNucleoFactoryInventoryAdapter` reads only two fixed TOML metadata files and checks a fixed list of
known tooling entrypoints. It does not recurse through applications, read source files, inspect
credentials, parse logs, access data, or copy private content. Output contains aggregate counts and
relative contract locations, never project identifiers or absolute paths.

## Current mapping

| Existing factory surface | Governor treatment |
|---|---|
| Factory self manifest | Read-only project context fact |
| Project catalog | Machine-readable aggregate adoption inventory |
| Golden Path tool | Partial normative source for project creation, not change policy |
| Factory status tool | Partial derived validator surface |
| Change Permit tool | Partial report-only workflow; not a persistent permit registry |
| Safety Gate tool | Partial command-risk gate; not actor authority |
| Capability registry | Not implemented; proposal is not treated as authority |
| Policy contract | No complete machine-readable contract currently defined |
| Authority registry | No machine-readable actor authority contract currently defined |
| Persistent permit registry | No schema-compatible registry currently defined |

## Fail-closed decision

The inventory adapter does not implement `GovernanceSource`. Adapting incomplete sources into that
interface would require fabricated defaults or invented paths. Full real-factory evaluation remains
disabled until the missing contracts are implemented or an explicit compatibility schema is
approved. The private factory was not modified.

```bash
governor inspect-factory /path/to/gonucleo --require-ready
```

Without the required contracts, inspection succeeds but `--require-ready` exits with code `9`.
