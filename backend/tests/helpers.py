import json

from app.agent.sources import FIXTURE
from app.models import Candidate


def fixture_candidates() -> list[Candidate]:
    return [Candidate.model_validate(c) for c in json.loads(FIXTURE.read_text())]
