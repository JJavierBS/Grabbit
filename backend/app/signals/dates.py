"""Cala dates come at day, month or year precision ("2019", "2019-06", "2019-06-01")."""

from __future__ import annotations

from datetime import date


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    parts = str(value)[:10].split("-")
    try:
        year = int(parts[0])
        month = int(parts[1]) if len(parts) > 1 else 1
        day = int(parts[2]) if len(parts) > 2 else 1
        return date(year, month, day)
    except (ValueError, IndexError):
        return None


def months_between(start: date, end: date) -> int:
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        months -= 1
    return months
