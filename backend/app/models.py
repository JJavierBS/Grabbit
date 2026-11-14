"""Shared API types, field for field from docs/agents/api.md "Shared types".

This module is the contract: the frontend types are generated from the OpenAPI schema
FastAPI builds from it. Change it together with api.md and `frontend/src/api/schema.ts`.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

TrustLevel = Literal[
    "filing", "primary", "press", "aggregator", "cala_news", "web_unverified", "not_published"
]
DatePrecision = Literal["day", "month", "year"]
InvestorRole = Literal["investor", "lender"]
SignalKind = Literal["co_invest", "lead_follow_on", "likely_to_raise"]
LinkKind = Literal["trusted_co_investor", "shared_investor"]
StyleLength = Literal["short", "medium", "long"]
StyleDetail = Literal["plain", "technical"]
Cadence = Literal["event", "daily", "weekly"]
AlertThreshold = Literal["low", "medium", "high"]
ChangeAuthor = Literal["user", "agent"]
ChatRole = Literal["user", "agent"]
ReportKind = Literal["prep", "digest", "memo"]
AlertKind = Literal[
    "new_round",
    "executive_change",
    "headcount_jump",
    "acquisition",
    "status_change",
    "web_news",
]
CalaMode = Literal["live", "replay"]
LLMMode = Literal["gemini", "fake"]

FactScalar = bool | int | float | str
FactValue = FactScalar | list[FactScalar]


class ApiModel(BaseModel):
    # Responses always carry every field, so generated frontend types mark them required.
    model_config = ConfigDict(extra="forbid", json_schema_serialization_defaults_required=True)


class Source(ApiModel):
    name: str
    url: str | None = None
    date: str | None = Field(default=None, description="ISO 8601; read it at date_precision")
    date_precision: DatePrecision | None = None
    rank: TrustLevel


class Fact(ApiModel):
    """A value with its provenance. Absent in Cala: value=None, trust=not_published."""

    value: FactValue | None = None
    unit: str | None = None
    trust: TrustLevel
    sources: list[Source] = Field(default_factory=list)

    @classmethod
    def not_published(cls) -> "Fact":
        return cls(value=None, trust="not_published", sources=[])


class Investor(ApiModel):
    entity_id: str
    name: str
    is_lead: bool
    role: InvestorRole


class Round(ApiModel):
    entity_id: str
    label: str | None = None
    name: str
    amount: Fact
    date: Fact
    investors: list[Investor]


class Signal(ApiModel):
    kind: SignalKind
    label: str
    value: FactValue | None = Field(default=None, description="None means not enough data")
    explanation: str
    facts: list[Fact]


class NewsEntity(ApiModel):
    entity_id: str
    name: str
    entity_type: str


class LinkNode(ApiModel):
    """A Cala entity on the path that proves a hidden link."""

    entity_id: str
    name: str
    entity_type: str


class NewsItem(ApiModel):
    """A news row from Cala's knowledge query: no per-item source, so trust is `cala_news`."""

    title: str
    summary: str | None = None
    date: Fact = Field(description="Read at its source's date_precision; absent when Cala has none")
    entities: list[NewsEntity] = Field(default_factory=list, description="Mentioned in the item")
    trust: TrustLevel = "cala_news"


class LinkEdge(ApiModel):
    """A Cala relationship between two path nodes, in Cala's own direction."""

    source: str
    target: str
    relationship: str
    role: str | None = None


class HiddenLink(ApiModel):
    """A second-degree relationship in Cala's graph that one company page does not show."""

    kind: LinkKind
    label: str
    explanation: str
    via_entity_id: str = Field(description="Investor on the candidate's own path it branches from")
    target: LinkNode
    count: int = Field(description="Rounds that prove it")
    trust: TrustLevel = Field(description="Weakest edge in the path: the link holds only if all do")
    nodes: list[LinkNode]
    edges: list[LinkEdge]
    facts: list[Fact]


class Candidate(ApiModel):
    entity_id: str
    name: str
    website: str | None = None
    description: str | None = None
    founding_date: Fact
    funding_stage: Fact
    headcount: Fact
    total_funding: Fact
    hq: Fact
    industries: list[str]
    rounds: list[Round]
    signals: list[Signal]
    news: list[NewsItem] = Field(
        default_factory=list, description="Latest news from Cala, newest first (cala_news)"
    )
    links: list[HiddenLink] = Field(default_factory=list)


class ProfileFilters(ApiModel):
    stages: list[str]
    sectors_in: list[str]
    sectors_out: list[str]
    countries: list[str]
    headcount_max: int | None = None
    ticket: Fact | None = None


class ReferenceInvestor(ApiModel):
    entity_id: str
    name: str


class ProfileStyle(ApiModel):
    length: StyleLength
    detail: StyleDetail
    language: str
    sections: list[str]


class Profile(ApiModel):
    version: int
    event_id: str | None = None
    thesis: str
    filters: ProfileFilters
    reference_investors: list[ReferenceInvestor]
    style: ProfileStyle
    cadence: Cadence
    alert_threshold: AlertThreshold
    sources: list[str] = Field(
        default_factory=list,
        description="Publisher domains the angel trusts; Context.dev allow-list (web, unverified)",
    )
    instructions: str
    updated_at: datetime


class ProfileChange(ApiModel):
    version: int
    field: str
    before: Any
    after: Any
    reason: str
    by: ChangeAuthor


class GraphNode(ApiModel):
    """A Cala entity the agent reached while answering in chat."""

    entity_id: str
    name: str
    entity_type: str
    facts: dict[str, Fact] = Field(
        default_factory=dict, description="Key properties, only for nodes the agent expanded"
    )


class GraphEdge(ApiModel):
    """A Cala relationship, pointing the way Cala stores it (investor -> round)."""

    source: str
    target: str
    relationship: str = Field(description="Cala relationship name, e.g. FOUNDED")
    role: str | None = None
    is_lead: bool = False
    facts: dict[str, Fact] = Field(
        default_factory=dict, description="Dated edge attributes (event_date, valid_since...)"
    )


class ExploredGraph(ApiModel):
    """The part of Cala's graph the agent walked for one chat answer."""

    nodes: list[GraphNode]
    edges: list[GraphEdge]


class ChatMessage(ApiModel):
    id: str
    role: ChatRole
    text: str
    created_at: datetime
    profile_changes: list[ProfileChange]
    report_id: str | None = None
    ui: str | None = Field(
        default=None, description="OpenUI Lang drawn with Cala components under the text"
    )
    graph: ExploredGraph | None = Field(
        default=None, description="Cala entities and edges the agent walked for this answer"
    )


class ReportSection(ApiModel):
    title: str
    body_md: str
    candidate_ids: list[str]


class Report(ApiModel):
    id: str
    kind: ReportKind
    created_at: datetime
    profile_version: int
    summary: str
    sections: list[ReportSection]
    candidates: list[Candidate]


class Alert(ApiModel):
    id: str
    created_at: datetime
    entity_id: str
    entity_name: str
    kind: AlertKind
    title: str
    why_it_matters: str
    importance: float = Field(ge=0, le=1)
    facts: list[Fact]
    simulated: bool


class Health(ApiModel):
    status: Literal["ok"]
    cala_mode: CalaMode
    llm_mode: LLMMode
    demo_mode: bool


class ChatRequest(ApiModel):
    text: str = Field(min_length=1, max_length=4000)


class ReportRunRequest(ApiModel):
    kind: ReportKind


class SimulateEventRequest(ApiModel):
    fixture: str = Field(pattern=r"^[a-z0-9_-]{1,64}$")


class ReportRef(ApiModel):
    id: str


class ErrorDetail(ApiModel):
    code: str
    message: str


class ErrorResponse(ApiModel):
    error: ErrorDetail
