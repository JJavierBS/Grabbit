"""Tools the agent may call to edit the profile and its own instructions."""

import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.agent.rules import violations
from app.llm import ToolCall, ToolSpec
from app.models import Fact, Profile, ProfileChange, ReferenceInvestor, Source

DOMAIN = re.compile(r"(?:[a-z0-9-]+\.)+[a-z]{2,}")


def _domain(value: str) -> str:
    value = value.strip().lower().removeprefix("https://").removeprefix("http://")
    return value.removeprefix("www.").split("/")[0]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TicketPatch(_Strict):
    value: float = Field(gt=0)
    unit: str = Field(default="EUR", min_length=3, max_length=3)


class FiltersPatch(_Strict):
    stages: list[str] | None = None
    sectors_in: list[str] | None = None
    sectors_out: list[str] | None = None
    countries: list[str] | None = None
    headcount_max: int | None = Field(default=None, gt=0)
    ticket: TicketPatch | None = None


class StylePatch(_Strict):
    length: Literal["short", "medium", "long"] | None = None
    detail: Literal["plain", "technical"] | None = None
    language: str | None = Field(default=None, min_length=2, max_length=5)
    sections: list[str] | None = None


class ReferenceInvestorPatch(_Strict):
    name: str = Field(min_length=1, max_length=120)
    entity_id: str | None = None


class ProfilePatch(_Strict):
    thesis: str | None = Field(default=None, max_length=1000)
    event_id: str | None = None
    filters: FiltersPatch | None = None
    reference_investors: list[ReferenceInvestorPatch] | None = None
    style: StylePatch | None = None
    cadence: Literal["event", "daily", "weekly"] | None = None
    alert_threshold: Literal["low", "medium", "high"] | None = None
    sources: list[str] | None = None

    @field_validator("sources")
    @classmethod
    def _domains(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        domains = [_domain(v) for v in value]
        if not all(DOMAIN.fullmatch(d) for d in domains):
            raise ValueError("sources must be publisher domains like techcrunch.com")
        return list(dict.fromkeys(domains))


class UpdateProfileArgs(_Strict):
    patch: ProfilePatch
    reason: str = Field(min_length=3, max_length=200)


class RewriteInstructionsArgs(_Strict):
    text: str = Field(max_length=1500)
    reason: str = Field(min_length=3, max_length=200)


_REASON = {
    "type": "string",
    "description": "One short line phrased as what changes from now on, in the investor's "
    "language, e.g. 'co-investors first, two lines per startup'. Shown to the investor.",
}
_STRINGS = {"type": "array", "items": {"type": "string"}}

TOOL_SPECS = [
    ToolSpec(
        name="update_profile",
        description="Edit structured profile fields. Send only the fields that change; lists "
        "replace the old list entirely, so send the full new list.",
        parameters={
            "type": "object",
            "properties": {
                "patch": {
                    "type": "object",
                    "properties": {
                        "thesis": {"type": "string"},
                        "filters": {
                            "type": "object",
                            "properties": {
                                "stages": _STRINGS,
                                "sectors_in": _STRINGS,
                                "sectors_out": _STRINGS,
                                "countries": {
                                    **_STRINGS,
                                    "description": "Countries or regions the startups must be "
                                    "based in, e.g. ['Finland'] or ['Europe'] or ['Nordics']. "
                                    "Set it whenever the investor names a place.",
                                },
                                "headcount_max": {"type": "integer"},
                                "ticket": {
                                    "type": "object",
                                    "properties": {
                                        "value": {"type": "number"},
                                        "unit": {"type": "string", "description": "ISO 4217"},
                                    },
                                    "required": ["value"],
                                },
                            },
                        },
                        "reference_investors": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {"name": {"type": "string"}},
                                "required": ["name"],
                            },
                        },
                        "style": {
                            "type": "object",
                            "properties": {
                                "length": {"type": "string", "enum": ["short", "medium", "long"]},
                                "detail": {"type": "string", "enum": ["plain", "technical"]},
                                "language": {"type": "string", "description": "ISO 639-1"},
                                "sections": _STRINGS,
                            },
                        },
                        "cadence": {"type": "string", "enum": ["event", "daily", "weekly"]},
                        "alert_threshold": {"type": "string", "enum": ["low", "medium", "high"]},
                        "sources": {
                            **_STRINGS,
                            "description": "Publisher domains the investor trusts for news "
                            "(e.g. techcrunch.com); read as web, unverified signals",
                        },
                    },
                },
                "reason": _REASON,
            },
            "required": ["patch", "reason"],
        },
    ),
    ToolSpec(
        name="rewrite_instructions",
        description="Replace your own report instructions: free text describing how this "
        "investor wants reports (order, length, what to skip, tone). Send the complete new "
        "text, keeping what still applies. Never include anything that breaks the fixed rules.",
        parameters={
            "type": "object",
            "properties": {"text": {"type": "string"}, "reason": _REASON},
            "required": ["text", "reason"],
        },
    ),
]


class ToolOutcome(BaseModel):
    applied: bool
    profile: Profile
    changes: list[ProfileChange] = Field(default_factory=list)
    reason: str = ""
    refusal: str | None = None
    error: str | None = None


def apply_tool_call(profile: Profile, call: ToolCall, by: Literal["user", "agent"]) -> ToolOutcome:
    """Validate a tool call and return the profile it would produce. Nothing is stored here."""
    try:
        if call.name == "update_profile":
            args = UpdateProfileArgs.model_validate(call.args)
            updated = _merge(profile, args.patch)
            reason = args.reason
        elif call.name == "rewrite_instructions":
            args = RewriteInstructionsArgs.model_validate(call.args)
            broken = violations(args.text)
            if broken:
                return ToolOutcome(
                    applied=False, profile=profile, refusal="; ".join(r.summary for r in broken)
                )
            updated = profile.model_copy(update={"instructions": args.text.strip()})
            reason = args.reason
        else:
            return ToolOutcome(applied=False, profile=profile, error=f"unknown tool {call.name}")
    except ValidationError as exc:
        return ToolOutcome(applied=False, profile=profile, error=_short(exc))

    changes = [
        ProfileChange(version=profile.version + 1, field=f, before=b, after=a, reason=reason, by=by)
        for f, b, a in diff(profile, updated)
    ]
    return ToolOutcome(applied=bool(changes), profile=updated, changes=changes, reason=reason)


def diff(before: Profile, after: Profile) -> list[tuple[str, Any, Any]]:
    """Changed leaves as (dotted field, before, after); lists compare as a whole."""
    skip = {"version", "updated_at"}
    old, new = before.model_dump(mode="json"), after.model_dump(mode="json")
    out: list[tuple[str, Any, Any]] = []
    for key in new:
        if key in skip or old.get(key) == new[key]:
            continue
        if isinstance(new[key], dict) and isinstance(old.get(key), dict) and key != "ticket":
            out.extend(
                (f"{key}.{sub}", old[key].get(sub), new[key][sub])
                for sub in new[key]
                if old[key].get(sub) != new[key][sub]
            )
        else:
            out.append((key, old.get(key), new[key]))
    return out


def _merge(profile: Profile, patch: ProfilePatch) -> Profile:
    data = profile.model_dump()
    fields = patch.model_dump(exclude_unset=True)
    for key in ("filters", "style"):
        if key in fields:
            data[key] = {**data[key], **(fields.pop(key) or {})}
    ticket = data["filters"].get("ticket")
    if isinstance(ticket, dict) and "trust" not in ticket:
        # A ticket stated in chat comes from the investor, not from Cala.
        data["filters"]["ticket"] = Fact(
            value=ticket["value"],
            unit=ticket.get("unit", "EUR"),
            trust="primary",
            sources=[Source(name="Investor, in chat", rank="primary")],
        )
    if "reference_investors" in fields:
        data["reference_investors"] = [
            ReferenceInvestor(
                # Team 2 resolves names to Cala entities; until then the id marks it unresolved.
                entity_id=r.get("entity_id") or f"unresolved:{r['name'].strip().lower()}",
                name=r["name"].strip(),
            )
            for r in fields.pop("reference_investors") or []
        ]
    data.update(fields)
    return Profile.model_validate(data)


def _short(exc: ValidationError) -> str:
    first = exc.errors()[0]
    return f"invalid {'.'.join(str(p) for p in first['loc'])}: {first['msg']}"
