"""Deterministic stand-in for Gemini, replaying scripts from app/fixtures/llm/."""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.llm.types import ChatResult, LLMError, Message, OnText, T, ToolCall, ToolSpec

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "llm"


class Script(BaseModel):
    """One scripted answer. Empty `match` is the task's fallback."""

    task: str
    match: list[str] = Field(default_factory=list)
    text: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)
    output: dict[str, Any] | None = None


class FakeLLM:
    def __init__(
        self, scripts: list[Script] | None = None, scripts_dir: Path = SCRIPTS_DIR
    ) -> None:
        self.scripts = scripts if scripts is not None else load_scripts(scripts_dir)
        self.calls: list[tuple[str, str]] = []

    async def chat(
        self,
        *,
        system: str,
        messages: list[Message],
        tools: list[ToolSpec] | None = None,
        on_text: OnText | None = None,
    ) -> ChatResult:
        last_user = next(
            (
                "\n".join([*(r.output for r in m.tool_results), m.text])
                for m in reversed(messages)
                if m.role == "user"
            ),
            "",
        )
        self.calls.append(("chat", last_user))
        task = "chat" if tools else "chat_followup"
        # The Cala walk in app/agent/explore.py has its own scripts.
        if tools and any(t.name.startswith("cala_") for t in tools):
            task = "explore"
        script = self._find(task, last_user) or self._find("chat", last_user)
        if script is None:
            return ChatResult(text="Noted.")
        if on_text and script.text:
            # Line by line, the way an answer streams in.
            lines = script.text.splitlines(keepends=True)
            for i in range(1, len(lines) + 1):
                on_text("".join(lines[:i]))
        return ChatResult(text=script.text, tool_calls=script.tool_calls if tools else [])

    async def generate(
        self, *, task: str, system: str, prompt: str, schema: type[T], quick: bool = False
    ) -> T:
        self.calls.append((task, prompt))
        script = self._find(task, prompt)
        if script is None or script.output is None:
            raise LLMError(f"FakeLLM has no script for task {task!r}")
        return schema.model_validate(script.output)

    async def transcribe(self, *, audio: bytes, mime_type: str) -> str:
        self.calls.append(("transcribe", mime_type))
        script = self._find("transcribe", "")
        return script.text if script else ""

    def _find(self, task: str, text: str) -> Script | None:
        lowered = text.lower()
        fallback = None
        for script in self.scripts:
            if script.task != task:
                continue
            if not script.match:
                fallback = fallback or script
            elif any(m.lower() in lowered for m in script.match):
                return script
        return fallback


def load_scripts(directory: Path = SCRIPTS_DIR) -> list[Script]:
    scripts: list[Script] = []
    for path in sorted(directory.glob("*.json")):
        scripts.extend(Script.model_validate(s) for s in json.loads(path.read_text()))
    return scripts
