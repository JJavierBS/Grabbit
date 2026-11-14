from fastapi import APIRouter

from app import events
from app.api.errors import ApiError
from app.models import Profile, ProfileChange
from app.references import resolve_references
from app.services import on_profile_change
from app.store import profile as profile_store
from app.store import reports as report_store

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("")
def get_profile() -> Profile:
    """With names typed in chat linked to Cala ids, so the page can mark investors you trust."""
    latest = report_store.latest()
    return resolve_references(profile_store.current(), latest.candidates if latest else [])


@router.get("/history")
def get_profile_history() -> list[ProfileChange]:
    return profile_store.history()


@router.post("/undo")
async def undo_profile_change() -> Profile:
    profile = profile_store.undo()
    if profile is None:
        raise ApiError(409, "nothing_to_undo", "The profile has no change to undo.")
    events.publish("profile", profile)
    await on_profile_change(profile)
    return profile
