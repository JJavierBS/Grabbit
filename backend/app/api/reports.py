from fastapi import APIRouter

from app.api.errors import ApiError
from app.models import Report, ReportRunRequest
from app.reports import service
from app.store import reports as report_store

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/latest")
async def latest() -> Report:
    report = report_store.latest()
    if report is None:
        raise ApiError(404, "no_report", "No report has been generated yet.")
    return report


@router.post("/run")
async def run(body: ReportRunRequest) -> Report:
    return await service.run(body.kind)
