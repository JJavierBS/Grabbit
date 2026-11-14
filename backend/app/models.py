"""Shared API types. Source of truth for the contract in docs/agents/api.md."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

TrustLevel = Literal["filing", "primary", "press", "aggregator", "web_unverified", "not_published"]
FactValue = str | float | int | bool | list[str] | None


class Source(BaseModel):
    name: str
    url: str | None = None
    date: str | None = None
    date_precision: Literal["day", "month", "year"] | None = None
    rank: TrustLevel


class Fact(BaseModel):
    value: FactValue = None
    unit: str | None = None
    trust: TrustLevel = "not_published"
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
    amount: Fact = Field(default_factory=Fact)
    date: Fact = Field(default_factory=Fact)
    investors: list[Investor] = Field(default_factory=list)


class Signal(BaseModel):
    kind: Literal["co_invest", "lead_follow_on", "likely_to_raise"]
    label: str
    value: FactValue | list[dict] | float = None
    explanation: str
    facts: list[Fact] = Field(default_factory=list)


class Candidate(BaseModel):
    entity_id: str
    name: str
    website: str | None = None
    description: str | None = None
    founding_date: Fact = Field(default_factory=Fact)
    funding_stage: Fact = Field(default_factory=Fact)
    headcount: Fact = Field(default_factory=Fact)
    total_funding: Fact = Field(default_factory=Fact)
    hq: Fact = Field(default_factory=Fact)
    industries: list[str] = Field(default_factory=list)
    rounds: list[Round] = Field(default_factory=list)
    signals: list[Signal] = Field(default_factory=list)


class Filters(BaseModel):
    stages: list[str] = Field(default_factory=list)
    sectors_in: list[str] = Field(default_factory=list)
    sectors_out: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)
    headcount_max: int | None = None
    ticket: Fact | None = None


class ReferenceInvestor(BaseModel):
    entity_id: str
    name: str


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
    updated_at: datetime


class ProfileChange(BaseModel):
    version: int
    field: str
    before: object = None
    after: object = None
    reason: str
    by: Literal["user", "agent"]


class ChatMessage(BaseModel):
    id: str
    role: Literal["user", "agent"]
    text: str
    created_at: datetime
    profile_changes: list[ProfileChange] = Field(default_factory=list)
    report_id: str | None = None


class ChatRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


class ReportSection(BaseModel):
    title: str
    body_md: str
    candidate_ids: list[str] = Field(default_factory=list)


class Report(BaseModel):
    id: str
    kind: Literal["prep", "digest", "memo"]
    created_at: datetime
    profile_version: int
    summary: str
    sections: list[ReportSection] = Field(default_factory=list)
    candidates: list[Candidate] = Field(default_factory=list)


class ReportRunRequest(BaseModel):
    kind: Literal["prep", "digest", "memo"] = "prep"


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
