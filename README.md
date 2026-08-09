# 🛡️ shesha-audit

**Append-only, hash-chained audit log + policy gate for Shesha.**

Every action an agent takes passes through `check(actor, tool, args)`, which
returns allow/confirm/deny and records the decision. Executions are recorded
too. Each event is chained to the previous by SHA-256 so tampering is
detectable via `verify_integrity()`.

- License: GPL-3.0
- Layer: Brain (governance)
- Part of: [Shesha ecosystem](https://github.com/gaganjainse/shesha-ecosystem)

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
uv run shesha-audit-mcp
```

Events live in `~/.local/share/shesha/audit/events.jsonl`.
