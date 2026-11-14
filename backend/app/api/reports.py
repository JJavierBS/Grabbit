from fastapi import APIRouter

from app.api.errors import ApiError
from app.models import Report, ReportRunRequest
from app.reports import service
from app.store import reports as report_store

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("")
def list_reports() -> list[Report]:
    """Past reports, newest first, at most 20."""
    return report_store.recent(20)


@router.get("/latest")
def get_latest_report() -> Report:
    report = report_store.latest()
    if report is None:
        raise ApiError(404, "no_report", "No report has been generated yet.")
    return report


@router.post("/run")
async def run_report(request: ReportRunRequest) -> Report:
    return await service.run(request.kind)
