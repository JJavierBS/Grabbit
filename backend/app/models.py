"""Shared types, field for field from docs/agents/api.md "Shared types"."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

TrustLevel = Literal["filing", "primary", "press", "aggregator", "web_unverified", "not_published"]
DatePrecision = Literal["day", "month", "year"]


class Source(BaseModel):
    name: str
    url: str | None = None
    date: str | None = None
    date_precision: DatePrecision | None = None
    rank: TrustLevel


class Fact(BaseModel):
    value: Any = None
    unit: str | None = None
    trust: TrustLevel
    sources: list[Source] = Field(default_factory=list)


class Investor(BaseModel):
    entity_id: str
    name: str
    is_lead: bool = False
    role: Literal["investor", "lender"] = "investor"


class Round(BaseModel):
    entity_id: str
    label: str | None = None
    name: str
    amount: Fact
    date: Fact
    investors: list[Investor] = Field(default_factory=list)


class Signal(BaseModel):
    kind: Literal["co_invest", "lead_follow_on", "likely_to_raise"]
    label: str
    value: Any = None
    explanation: str
    facts: list[Fact] = Field(default_factory=list)


class Candidate(BaseModel):
    entity_id: str
    name: str
    website: str | None = None
    description: str | None = None
    founding_date: Fact
    funding_stage: Fact
    headcount: Fact
    total_funding: Fact
    hq: Fact
    industries: list[str] = Field(default_factory=list)
    rounds: list[Round] = Field(default_factory=list)
    signals: list[Signal] = Field(default_factory=list)


class ReferenceInvestor(BaseModel):
    entity_id: str
    name: str


class Filters(BaseModel):
    stages: list[str] = Field(default_factory=list)
    sectors_in: list[str] = Field(default_factory=list)
    sectors_out: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)
    headcount_max: int | None = None
    ticket: Fact | None = None


class Style(BaseModel):
    length: Literal["short", "medium", "long"] = "medium"
    detail: Literal["plain", "technical"] = "plain"
    language: str = "en"
    sections: list[str] = Field(default_factory=list)


class Profile(BaseModel):
    version: int = 1
    event_id: str | None = None
    thesis: str = ""
    filters: Filters = Field(default_factory=Filters)
    reference_investors: list[ReferenceInvestor] = Field(default_factory=list)
    style: Style = Field(default_factory=Style)
    cadence: Literal["event", "daily", "weekly"] = "event"
    alert_threshold: Literal["low", "medium", "high"] = "medium"
    instructions: str = ""
    updated_at: datetime | None = None


class Alert(BaseModel):
    id: str
    created_at: datetime
    entity_id: str
    entity_name: str
    kind: Literal[
        "new_round",
        "executive_change",
        "headcount_jump",
        "acquisition",
        "status_change",
        "web_news",
    ]
    title: str
    why_it_matters: str
    importance: float = Field(ge=0, le=1)
    facts: list[Fact] = Field(default_factory=list)
    simulated: bool = False
