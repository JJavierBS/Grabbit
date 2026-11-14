"""Inputs the agent reads from other teams' modules, behind one seam."""

from pydantic import TypeAdapter

from app import fixtures
from app.models import Candidate, Profile


def fixture_candidates() -> list[Candidate]:
    return TypeAdapter(list[Candidate]).validate_python(fixtures.load_json("candidates.json"))


async def candidates_for(profile: Profile) -> list[Candidate]:
    # TODO(#23): read the Slush discovery pipeline once it lands; fixtures until then.
    return fixture_candidates()
