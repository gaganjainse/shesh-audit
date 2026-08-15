>  **Consolidated into [shesh-core](https://github.com/gaganjainse/shesh-core)** — this module now lives in the shesh-core monorepo (same package name, same console script). Archived 2026-08-13.

# shesh-audit

**Append-only, hash-chained audit log + policy gate for Shesh.**

Every action an agent takes passes through `check(actor, tool, args)`, which
returns allow/confirm/deny and records the decision. Executions are recorded
too. Each event is chained to the previous by SHA-256 so tampering is
detectable via `verify_integrity()`.

- License: GPL-3.0
- Layer: Brain (governance)
- Part of: [Shesh ecosystem](https://github.com/gaganjainse/shesh-ecosystem)

## Defaults

- Read-only tools (`get_*`, `list_*`, `search*`, `recall`) → allow.
- Protected paths (job data, `.ssh`, `.gnupg`, vaults) → deny.
- Everything else → confirm.
- Rules are runtime-extensible and prepend (first match wins).

## MCP tools

- `check`, `record_execution`, `recent_events`, `verify_integrity`, `add_rule`

## Develop

```bash
uv sync --extra dev
uv run pytest -q        # 10 offline tests
uv run ruff check .
uv run shesh-audit-mcp
```
Events live in `~/.local/share/shesh/audit/events.jsonl`.

## Security

Security posture and vulnerability reporting: [canonical ecosystem security
policy](https://github.com/gaganjainse/shesh-ecosystem/blob/main/SECURITY.md).
