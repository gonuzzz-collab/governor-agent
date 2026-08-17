"""Deterministic Strands model double for offline tests and reproducible demos.

This model exercises the real Strands agent loop and custom-tool machinery. It is not presented as
an intelligent production model and cannot make governance decisions.
"""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator, AsyncIterable, Callable
from typing import Any, TypeVar

from pydantic import BaseModel
from strands.models import Model
from strands.types.content import Messages, SystemContentBlock
from strands.types.streaming import StreamEvent
from strands.types.tools import ToolChoice, ToolSpec

from governor_agent.agent.models import AgentGovernanceReport

T = TypeVar("T", bound=BaseModel)


class DeterministicGovernorModel(Model):
    """Select the required Governor tools in a fixed, inspectable order."""

    TOOL_ORDER = (
        "inspect_change_request",
        "inspect_governance",
        "evaluate_change_request",
    )

    def __init__(self, report_supplier: Callable[[], AgentGovernanceReport]) -> None:
        self._config: dict[str, Any] = {
            "model_id": "governor-offline-deterministic",
            "context_window_limit": 16_000,
        }
        self._report_supplier = report_supplier
        self._counter = 0

    def update_config(self, **model_config: Any) -> None:
        self._config.update(model_config)

    def get_config(self) -> dict[str, Any]:
        return dict(self._config)

    async def structured_output(
        self,
        output_model: type[T],
        prompt: Messages,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[dict[str, T | Any], None]:
        del prompt, system_prompt, kwargs
        report = self._report_supplier()
        yield {"output": output_model.model_validate(report.model_dump(mode="json"))}

    async def stream(
        self,
        messages: Messages,
        tool_specs: list[ToolSpec] | None = None,
        system_prompt: str | None = None,
        *,
        tool_choice: ToolChoice | None = None,
        system_prompt_content: list[SystemContentBlock] | None = None,
        invocation_state: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> AsyncIterable[StreamEvent]:
        del system_prompt, tool_choice, system_prompt_content, invocation_state, kwargs
        available = {spec["name"] for spec in tool_specs or []}
        called = self._called_tools(messages)
        next_tool = next((name for name in self.TOOL_ORDER if name not in called), None)
        if next_tool is not None:
            if next_tool not in available:
                raise RuntimeError(f"required Governor tool is unavailable: {next_tool}")
            async for event in self._tool_call(next_tool, {}):
                yield event
            return

        output_name = AgentGovernanceReport.__name__
        if output_name not in available:
            raise RuntimeError("Strands structured output tool is unavailable")
        async for event in self._tool_call(
            output_name,
            self._report_supplier().model_dump(mode="json"),
        ):
            yield event

    @staticmethod
    def _called_tools(messages: Messages) -> tuple[str, ...]:
        return tuple(
            block["toolUse"]["name"]
            for message in messages
            if message["role"] == "assistant"
            for block in message["content"]
            if "toolUse" in block
        )

    async def _tool_call(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> AsyncGenerator[StreamEvent, None]:
        self._counter += 1
        tool_use_id = f"offline-tool-{self._counter:04d}"
        yield {"messageStart": {"role": "assistant"}}
        yield {
            "contentBlockStart": {"start": {"toolUse": {"name": name, "toolUseId": tool_use_id}}}
        }
        yield {
            "contentBlockDelta": {
                "delta": {"toolUse": {"input": json.dumps(arguments, sort_keys=True)}}
            }
        }
        yield {"contentBlockStop": {}}
        yield {"messageStop": {"stopReason": "tool_use"}}
        yield {
            "metadata": {
                "usage": {"inputTokens": 0, "outputTokens": 0, "totalTokens": 0},
                "metrics": {"latencyMs": 0},
            }
        }
