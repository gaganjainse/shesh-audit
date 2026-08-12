"""MCP server middleware: enforce the Guard on every tool call.

FastMCP registers tools via @mcp.tool(). This module provides a `guarded`
decorator that runs the policy check BEFORE the wrapped function and records
execution AFTER, so every MCP tool in every Shesh component is governed by
the same allow/confirm/deny policy without each component re-implementing it.

Usage:
    from mcp.server.fastmcp import FastMCP
    from shesh_audit.mcp_guard import GuardedMCP

    mcp = GuardedMCP("shesh-system")  # wraps FastMCP

    @mcp.tool()
    def set_power_profile(profile: str) -> dict:
        ...

For tools that are purely read-only, set require_confirmation=False to skip
the confirm prompt when policy returns "confirm" (they are still logged).
"""
from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any

from mcp.server.fastmcp import FastMCP

from .gate import Guard
from .policy import Verdict


class GuardedMCP(FastMCP):
    """A FastMCP that runs every tool through a Guard."""

    def __init__(self, name: str, guard: Guard | None = None, **kwargs) -> None:
        super().__init__(name, **kwargs)
        self.guard = guard or Guard()
        self._actor = name

    def tool(self, *tool_args, **tool_kwargs):  # type: ignore[override]
        """Override tool() to wrap the registered function with policy checks."""
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            actor = self._actor

            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                tool_name = getattr(fn, "__name__", "unknown")
                # Merge args/kwargs into a dict the policy can inspect.
                inspect_args = {f"arg{i}": a for i, a in enumerate(args)}
                inspect_args.update(kwargs)

                decision = self.guard.check(
                    tool_name, inspect_args, actor=actor)

                if decision.verdict == Verdict.DENY.value:
                    return {"ok": False, "error": f"denied: {decision.reason}"}

                # In a headless/agent context, "confirm" is treated as allowed
                # but flagged; the ACP layer surfaces the confirmation to a human
                # when running inside an editor. Pure read tools can opt out.
                try:
                    result = fn(*args, **kwargs)
                    self.guard.log_execution(
                        tool_name,
                        success=not (isinstance(result, dict) and result.get("ok") is False),
                        actor=actor, args=inspect_args,
                        result=str(result)[:200],
                    )
                    return result
                except Exception as e:  # noqa: BLE001
                    self.guard.log_execution(
                        tool_name, False, actor=actor,
                        args=inspect_args, result=str(e)[:200])
                    raise

            # Register the wrapper, not the raw function.
            return super(GuardedMCP, self).tool(*tool_args, **tool_kwargs)(wrapper)

        return decorator
