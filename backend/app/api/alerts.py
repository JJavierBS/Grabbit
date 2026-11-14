from fastapi import APIRouter

from app import fixtures
from app.models import Alert
from app.store.db import connect
from app.store.snapshots import WatchStore

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("")
def get_alerts() -> list[Alert]:
    """Alerts the watcher stored, newest first; the fixtures until it has produced any."""
    with connect() as conn:
        stored = WatchStore(conn).alerts()
    return stored or fixtures.alerts()
