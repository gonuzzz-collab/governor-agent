"""Low-noise Strands hook observability that records tool names, not payloads."""

from __future__ import annotations

from strands.hooks import AfterToolCallEvent, BeforeToolCallEvent, HookRegistry


class ToolTraceHook:
    """Record selected tool names without logging arguments or tool results."""

    def __init__(self) -> None:
        self.started: list[str] = []
        self.completed: list[str] = []

    def register_hooks(self, registry: HookRegistry, **kwargs: object) -> None:
        del kwargs
        registry.add_callback(BeforeToolCallEvent, self.before_tool)
        registry.add_callback(AfterToolCallEvent, self.after_tool)

    def before_tool(self, event: BeforeToolCallEvent) -> None:
        self.started.append(event.tool_use["name"])

    def after_tool(self, event: AfterToolCallEvent) -> None:
        self.completed.append(event.tool_use["name"])
