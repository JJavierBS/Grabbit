from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter

from app import fixtures
from app.events import publish
from app.models import Report, ReportRef, ReportRunRequest

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/latest")
def get_latest_report() -> Report:
    return fixtures.latest_report()


@router.post("/run")
def run_report(request: ReportRunRequest) -> Report:
    report = fixtures.latest_report().model_copy(
        update={
            "id": f"rep-{uuid4().hex[:12]}",
            "kind": request.kind,
            "created_at": datetime.now(UTC),
        }
    )
    publish("report", ReportRef(id=report.id))
    return report
