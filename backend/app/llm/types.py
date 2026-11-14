from typing import Any, Literal, Protocol, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    """The model could not be reached or returned something unusable."""


class ToolSpec(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any]


class ToolCall(BaseModel):
    name: str
    args: dict[str, Any] = Field(default_factory=dict)
    id: str | None = None
    # Gemini 3 rejects a replayed function call without the signature it was sent with.
    signature: bytes | None = None


class ToolResult(BaseModel):
    """What a tool returned, sent back to the model in a user turn."""

    name: str
    output: str
    id: str | None = None


class Message(BaseModel):
    """A turn. A model turn may carry the tool calls it made; the next user turn their results."""

    role: Literal["user", "model"]
    text: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)
    tool_results: list[ToolResult] = Field(default_factory=list)


class ChatResult(BaseModel):
    text: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)


class LLM(Protocol):
    async def chat(
        self, *, system: str, messages: list[Message], tools: list[ToolSpec] | None = None
    ) -> ChatResult: ...

    async def generate(self, *, task: str, system: str, prompt: str, schema: type[T]) -> T: ...
