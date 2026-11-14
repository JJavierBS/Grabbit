"""Turn raw Cala values into `Fact`s with their trust level (docs/agents/agent.md "Trust scale")."""

from __future__ import annotations

from typing import Any

from app.models import Fact, Source, TrustLevel

RANKS: dict[str, TrustLevel] = {
    "FILING": "filing",
    "PRIMARY": "primary",
    "PRESS": "press",
    "AGGREGATOR": "aggregator",
}
# Strongest first. A source without source_rank, or a value with no source at all, gets the
# weakest Cala level: we never claim more trust than Cala states.
STRENGTH: list[TrustLevel] = ["filing", "primary", "press", "aggregator"]
UNRANKED: TrustLevel = "aggregator"


def not_published() -> Fact:
    return Fact(value=None, trust="not_published", sources=[])


def to_source(raw: dict[str, Any], precision: str | None = None) -> Source:
    document = raw.get("document")
    url = document.get("endpoint") if isinstance(document, dict) else document
    return Source(
        name=raw.get("name") or "unknown",
        url=url or None,
        date=raw.get("date"),
        date_precision=raw.get("date_precision") or precision,
        rank=RANKS.get(str(raw.get("source_rank") or "").upper(), UNRANKED),
    )


def strongest(sources: list[Source]) -> TrustLevel:
    if not sources:
        return UNRANKED
    return min(sources, key=lambda s: STRENGTH.index(s.rank)).rank


def to_fact(
    value: Any,
    raw_sources: list[dict[str, Any]] | None,
    unit: str | None = None,
    precision: str | None = None,
) -> Fact:
    """Value plus sources. `None` means Cala did not return it: not published, never 0."""
    if value is None:
        return not_published()
    sources = [to_source(s, precision) for s in raw_sources or []]
    return Fact(value=_scalar(value), unit=unit, trust=strongest(sources), sources=sources)


def _scalar(value: Any) -> Any:
    """`Fact.value` is a scalar or a list of scalars (api.md); flatten anything richer."""
    if isinstance(value, bool | int | float | str):
        return value
    if isinstance(value, list):
        return [v if isinstance(v, bool | int | float | str) else str(v) for v in value]
    return str(value)


def property_fact(entity: dict[str, Any], name: str) -> Fact:
    """A node property as a Fact; `<name>_units` and `<name>__precision` are picked up."""
    props = entity.get("properties") or {}
    prop = props.get(name)
    if not isinstance(prop, dict):
        return not_published()
    unit_prop = props.get(f"{name}_units")
    unit = unit_prop.get("value") if isinstance(unit_prop, dict) else None
    precision = _plain(props.get(f"{name}__precision"))
    return to_fact(prop.get("value"), prop.get("sources"), unit=unit, precision=precision)


def edge_fact(edge: dict[str, Any], attr: str) -> Fact:
    """An attribute on a relationship (e.g. `event_date`), sourced by the edge's sources."""
    props = edge.get("properties") or {}
    value = _plain(props.get(attr))
    precision = _plain(props.get(f"{attr}__precision"))
    return to_fact(value, props.get("sources"), precision=precision)


def edge_attr(edge: dict[str, Any], attr: str) -> Any:
    return _plain((edge.get("properties") or {}).get(attr))


def relationships(entity: dict[str, Any], direction: str, rel_type: str) -> list[dict[str, Any]]:
    rels = (entity.get("relationships") or {}).get(direction) or {}
    return rels.get(rel_type) or []


def observations(entity: dict[str, Any], name_or_code: str) -> list[tuple[str, Any, Source]]:
    """Dated points of a time series, oldest first, each with its origin as a Source."""
    points: list[tuple[str, Any, Source]] = []
    for series in entity.get("numerical_observations") or []:
        props = series.get("properties") or {}
        if name_or_code not in (series.get("name"), series.get("id"), props.get("code")):
            continue
        for point in series.get("data") or []:
            origin = point.get("origin") or {}
            source = Source(
                name=origin.get("name") or origin.get("source") or "unknown",
                url=origin.get("url"),
                date=origin.get("published_time"),
                rank=RANKS.get(str(origin.get("source_rank") or "").upper(), UNRANKED),
            )
            points.append((point.get("time"), point.get("value"), source))
    return sorted(points, key=lambda p: p[0] or "")


def _plain(value: Any) -> Any:
    """Edge attributes come either bare or wrapped as {value, sources}."""
    if isinstance(value, dict) and "value" in value:
        return value["value"]
    return value
