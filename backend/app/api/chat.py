from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter

from app import fixtures
from app.models import ChatMessage, ChatRequest

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("")
def get_chat() -> list[ChatMessage]:
    return fixtures.chat()


@router.post("")
def post_chat(request: ChatRequest) -> ChatMessage:
    return ChatMessage(
        id=f"msg-{uuid4().hex[:12]}",
        role="agent",
        text=f'Noted: "{request.text}". (Mock reply until the agent lands, #25.)',
        created_at=datetime.now(UTC),
        profile_changes=[],
        report_id=None,
    )
