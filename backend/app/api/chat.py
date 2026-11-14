from fastapi import APIRouter

from app.agent import chat as agent_chat
from app.agent.sources import candidates_for
from app.llm import get_llm
from app.models import ChatMessage, ChatRequest
from app.services import latest_report_summary, on_profile_change
from app.store import chat as chat_store
from app.store import profile as profile_store

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("")
def get_chat() -> list[ChatMessage]:
    return chat_store.all_messages()


@router.post("")
async def post_chat(request: ChatRequest) -> ChatMessage:
    profile = profile_store.current()
    return await agent_chat.handle_message(
        request.text.strip(),
        llm=get_llm(),
        candidates=await candidates_for(profile),
        report_summary=latest_report_summary(),
        on_profile_change=on_profile_change,
    )
