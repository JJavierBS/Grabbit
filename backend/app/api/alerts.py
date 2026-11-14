from fastapi import APIRouter

from app import fixtures
from app.models import Alert

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("")
def get_alerts() -> list[Alert]:
    return fixtures.alerts()
