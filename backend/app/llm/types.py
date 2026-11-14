from typing import Any, Literal, Protocol, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    """The model could not be reached or returned something unusable."""


class Message(BaseModel):
    role: Literal["user", "model"]
    text: str


class ToolSpec(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any]


class ToolCall(BaseModel):
    name: str
    args: dict[str, Any] = Field(default_factory=dict)


class ChatResult(BaseModel):
    text: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)


class LLM(Protocol):
    async def chat(
        self, *, system: str, messages: list[Message], tools: list[ToolSpec] | None = None
    ) -> ChatResult: ...

    async def generate(self, *, task: str, system: str, prompt: str, schema: type[T]) -> T: ...
