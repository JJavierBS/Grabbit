"""Reports, newest last."""

from app import workspace
from app.models import Report
from app.store import db

db.register_table(
    """CREATE TABLE IF NOT EXISTS reports (
        seq INTEGER PRIMARY KEY AUTOINCREMENT,
        workspace TEXT NOT NULL,
        id TEXT UNIQUE NOT NULL,
        report_json TEXT NOT NULL
    )"""
)
db.drop_if_missing("reports", "workspace")


def add(report: Report) -> Report:
    with db.connect() as conn:
        conn.execute(
            "INSERT INTO reports (workspace, id, report_json) VALUES (?, ?, ?)",
            (workspace.current(), report.id, report.model_dump_json()),
        )
    return report


def latest() -> Report | None:
    with db.connect() as conn:
        row = conn.execute(
            "SELECT report_json FROM reports WHERE workspace = ? ORDER BY seq DESC LIMIT 1",
            (workspace.current(),),
        ).fetchone()
    return Report.model_validate_json(row["report_json"]) if row else None


def recent(limit: int = 20) -> list[Report]:
    """Stored reports, newest first."""
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT report_json FROM reports WHERE workspace = ? ORDER BY seq DESC LIMIT ?",
            (workspace.current(), limit),
        ).fetchall()
    return [Report.model_validate_json(r["report_json"]) for r in rows]


def get(report_id: str) -> Report | None:
    with db.connect() as conn:
        row = conn.execute(
            "SELECT report_json FROM reports WHERE workspace = ? AND id = ?",
            (workspace.current(), report_id),
        ).fetchone()
    return Report.model_validate_json(row["report_json"]) if row else None


def workspaces() -> list[str]:
    """Every workspace with a report: the ones the scheduled jobs have something to do for."""
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT workspace FROM reports GROUP BY workspace ORDER BY MIN(seq)"
        ).fetchall()
    return [r["workspace"] for r in rows]
