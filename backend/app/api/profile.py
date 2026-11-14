from fastapi import APIRouter

from app import fixtures
from app.events import publish
from app.models import Profile, ProfileChange

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("")
def get_profile() -> Profile:
    return fixtures.profile()


@router.get("/history")
def get_profile_history() -> list[ProfileChange]:
    return fixtures.profile_history()


@router.post("/undo")
def undo_profile_change() -> Profile:
    profile = fixtures.profile()
    publish("profile", profile)
    return profile
