from fastapi import APIRouter

from app.models import Alert
from app.store.db import connect
from app.store.snapshots import WatchStore

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("")
def get_alerts() -> list[Alert]:
    """Alerts the watcher or the staged demo event stored, newest first; none until then.

    Never the fixture alerts: they are made up, and this endpoint is public (#254).
    """
    with connect() as conn:
        return WatchStore(conn).alerts()
