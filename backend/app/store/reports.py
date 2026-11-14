"""Reports, newest last."""

from app.models import Report
from app.store import db

db.register_table(
    """CREATE TABLE IF NOT EXISTS reports (
        seq INTEGER PRIMARY KEY AUTOINCREMENT,
        id TEXT UNIQUE NOT NULL,
        report_json TEXT NOT NULL
    )"""
)


def add(report: Report) -> Report:
    with db.connect() as conn:
        conn.execute(
            "INSERT INTO reports (id, report_json) VALUES (?, ?)",
            (report.id, report.model_dump_json()),
        )
    return report


def latest() -> Report | None:
    with db.connect() as conn:
        row = conn.execute("SELECT report_json FROM reports ORDER BY seq DESC LIMIT 1").fetchone()
    return Report.model_validate_json(row["report_json"]) if row else None


def recent(limit: int = 20) -> list[Report]:
    """Stored reports, newest first."""
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT report_json FROM reports ORDER BY seq DESC LIMIT ?", (limit,)
        ).fetchall()
    return [Report.model_validate_json(r["report_json"]) for r in rows]


def get(report_id: str) -> Report | None:
    with db.connect() as conn:
        row = conn.execute("SELECT report_json FROM reports WHERE id = ?", (report_id,)).fetchone()
    return Report.model_validate_json(row["report_json"]) if row else None
