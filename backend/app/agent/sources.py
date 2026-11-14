"""Inputs the agent reads from other teams' modules, behind one seam."""

import json
from pathlib import Path

from app.models import Candidate, Profile

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "candidates.json"


async def candidates_for(profile: Profile) -> list[Candidate]:
    # TODO(#23): read the Slush discovery pipeline once it lands; fixtures until then.
    return [Candidate.model_validate(c) for c in json.loads(FIXTURE.read_text())]
