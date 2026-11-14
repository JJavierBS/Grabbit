"""A compact state per watched startup, and what changed between two of them.

Only changes worth an alert are reported (api.md `Alert.kind`). The first snapshot of a
company is a baseline: no alerts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.cala.normalize import edge_attr, observations, relationships
from app.models import Candidate

EXECUTIVE_EDGES = {"IS_CEO_OF": "CEO", "IS_CTO_OF": "CTO", "IS_VICEPRESIDENT_OF": "VP"}
HEADCOUNT_JUMP = 0.20


@dataclass
class Change:
    kind: str
    key: str
    title: str
    why: str
    data: dict[str, Any] = field(default_factory=dict)


def snapshot_of(company: dict[str, Any], candidate: Candidate) -> dict[str, Any]:
    props = company.get("properties") or {}
    executives = {}
    for rel, role in EXECUTIVE_EDGES.items():
        for edge in relationships(company, "incoming", rel):
            executives[f"{rel}:{edge['id']}"] = {
                "role": role,
                "name": edge.get("name"),
                "valid_until": edge_attr(edge, "valid_until"),
            }
    series = observations(company, "employee_count")
    headcount = series[-1][1] if series else candidate.headcount.value
    return {
        "name": candidate.name,
        "rounds": {
            r.entity_id: {
                "name": r.name,
                "date": r.date.value,
                "leads": [i.name for i in r.investors if i.is_lead],
                "lead_ids": [i.entity_id for i in r.investors if i.is_lead],
            }
            for r in candidate.rounds
        },
        "executives": executives,
        "headcount": headcount if isinstance(headcount, int | float) else None,
        "status": (props.get("operational_status") or {}).get("value"),
        "domains": {
            e.get("name"): edge_attr(e, "status")
            for e in relationships(company, "outgoing", "HAS_DOMAIN_NAME")
        },
        "acquisitions": {
            e["id"]: {
                "name": e.get("name"),
                "role": edge_attr(e, "role"),
                "date": edge_attr(e, "event_date"),
            }
            for e in relationships(company, "outgoing", "PARTICIPATES_IN_CORPORATE_EVENT")
            if e.get("entity_type") == "CorporateEvent"
        },
    }


def diff(old: dict[str, Any], new: dict[str, Any]) -> list[Change]:
    name = new.get("name") or "A shortlisted startup"
    changes: list[Change] = []

    for rid, r in new["rounds"].items():
        if rid in old.get("rounds", {}):
            continue
        led = f", led by {', '.join(r['leads'])}" if r["leads"] else ""
        changes.append(
            Change(
                "new_round",
                rid,
                f"{name} announced a {r['name']}{led}",
                "A new round changes its valuation and who has a seat at the table.",
                {"round_id": rid, "lead_ids": r["lead_ids"], "leads": r["leads"]},
            )
        )

    for key, person in new["executives"].items():
        before = old.get("executives", {}).get(key)
        if before is None and not person["valid_until"]:
            changes.append(
                Change(
                    "executive_change",
                    f"{key}:joined",
                    f"{person['name']} joined {name} as {person['role']}",
                    "A senior hire often comes before scaling or a new round.",
                    {"role": person["role"], "left": False},
                )
            )
        elif person["valid_until"] and not (before or {}).get("valid_until"):
            changes.append(
                Change(
                    "executive_change",
                    f"{key}:left",
                    f"{person['name']} left {name} as {person['role']}",
                    "A founder or executive leaving is a risk to check before investing.",
                    {"role": person["role"], "left": True},
                )
            )

    before, after = old.get("headcount"), new.get("headcount")
    if before and after and (after - before) / before >= HEADCOUNT_JUMP:
        changes.append(
            Change(
                "headcount_jump",
                f"headcount:{after:g}",
                f"{name} grew from {before:g} to {after:g} people",
                "Fast hiring usually means the company is preparing to raise or has just raised.",
                {"before": before, "after": after},
            )
        )

    for eid, event in new["acquisitions"].items():
        if eid not in old.get("acquisitions", {}):
            changes.append(
                Change(
                    "acquisition",
                    eid,
                    f"{name}: {str(event['name']).replace('_', ' ').lower()}",
                    "An acquisition can close the round or change the company entirely.",
                    {"event_id": eid, "role": event["role"]},
                )
            )

    if old.get("status") and new.get("status") != old.get("status"):
        changes.append(
            Change(
                "status_change",
                f"status:{new.get('status')}",
                f"{name} is now {new.get('status') or 'without a status'}",
                "A change in operating status needs checking before any meeting.",
                {"before": old.get("status"), "after": new.get("status")},
            )
        )
    for domain, status in new["domains"].items():
        was = old.get("domains", {}).get(domain)
        if str(status).upper() == "INACTIVE" and str(was).upper() == "ACTIVE":
            changes.append(
                Change(
                    "status_change",
                    f"domain:{domain}",
                    f"{name}'s website {domain} went inactive",
                    "A dead website can mean a pivot, a rebrand or a shutdown.",
                    {"domain": domain},
                )
            )
    return changes
