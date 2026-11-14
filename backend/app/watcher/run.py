"""Poll shortlisted startups, diff against their snapshot, score, store and deliver alerts.

Cala has no push or webhooks (docs/agents/flow.md section 4), so the watcher re-reads each
watched node with `fresh=True` and compares. `simulate` feeds a staged change from
`app/fixtures/demo_events/` through the same path; staged data never touches the Cala cache
or the stored snapshots.
"""

from __future__ import annotations

import copy
import hashlib
import inspect
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from app.cala.client import CalaCacheMiss, CalaError
from app.cala.normalize import edge_fact, property_fact, relationships
from app.discovery.build import build_candidate, build_round, issuer_round_ids
from app.discovery.pipeline import ROUND_BODY, Cala, fetch_company
from app.models import Alert, Candidate, Fact, Profile
from app.store.snapshots import WatchStore
from app.watcher.importance import Scorer, passes, score
from app.watcher.snapshot import EXECUTIVE_EDGES, Change, diff, snapshot_of

log = logging.getLogger(__name__)

DEMO_EVENTS = Path(__file__).resolve().parent.parent / "fixtures" / "demo_events"

# Team 1's events bus: publish(kind, payload); may be sync or async.
Publish = Callable[[str, dict[str, Any]], Any]


@dataclass
class Watcher:
    client: Cala
    store: WatchStore
    publish: Publish | None = None
    scorer: Scorer | None = None
    clock: Callable[[], datetime] = field(default=lambda: datetime.now(UTC))
    max_alerts_per_day: int = 5
    max_rounds_per_company: int = 10

    async def run_once(self, profile: Profile, shortlist: list[str]) -> list[Alert]:
        alerts: list[Alert] = []
        for entity_id in shortlist:
            try:
                company = await fetch_company(self.client, entity_id, fresh=True)
                candidate = await self._candidate(company)
            except (CalaError, CalaCacheMiss) as err:
                # One unreadable company must not leave the rest of the shortlist unwatched.
                log.warning("watcher skipped %s: %s", entity_id, err)
                continue
            alerts += await self._process(company, candidate, profile, simulated=False)
        return alerts

    async def simulate(self, fixture: str, profile: Profile) -> list[Alert]:
        """Replay a staged change (labelled `simulated`) through the real alert path."""
        staged = json.loads((DEMO_EVENTS / f"{Path(fixture).stem}.json").read_text())
        entity_id = staged["entity_id"]
        base = await fetch_company(self.client, entity_id)
        if self.store.snapshot(entity_id) is None:
            self.store.save_snapshot(
                entity_id, snapshot_of(base, await self._candidate(base)), self.clock()
            )
        patched = merge(base, staged.get("patch") or {})
        candidate = await self._candidate(patched, staged.get("rounds") or {})
        return await self._process(patched, candidate, profile, simulated=True)

    async def _candidate(
        self, company: dict[str, Any], staged_rounds: dict[str, Any] | None = None
    ) -> Candidate:
        rounds = []
        for rid in issuer_round_ids(company)[: self.max_rounds_per_company]:
            node = (staged_rounds or {}).get(rid) or await self.client.retrieve(rid, ROUND_BODY)
            rounds.append(build_round(node))
        return build_candidate(company, rounds)

    async def _process(
        self, company: dict[str, Any], candidate: Candidate, profile: Profile, *, simulated: bool
    ) -> list[Alert]:
        now = self.clock()
        new = snapshot_of(company, candidate)
        old = self.store.snapshot(candidate.entity_id)
        if old is None:
            if not simulated:
                self.store.save_snapshot(candidate.entity_id, new, now)
            return []  # first look at this company: baseline only
        delivered: list[Alert] = []
        deferred = False
        for change in diff(old, new):
            # Real alerts dedupe on the change; a staged one can be replayed in rehearsals.
            salt = now.isoformat() if simulated else "real"
            alert_id = _alert_id(candidate.entity_id, change, salt)
            if self.store.has_alert(alert_id):
                continue
            value, reason = await score(change, profile, self.scorer)
            if not passes(value, profile):
                continue
            if not simulated:
                sent_today = self.store.alerts_since(now - timedelta(days=1), simulated=False)
                if sent_today >= self.max_alerts_per_day:
                    deferred = True
                    continue
            alert = Alert(
                id=alert_id,
                created_at=now,
                entity_id=candidate.entity_id,
                entity_name=candidate.name,
                kind=change.kind,  # type: ignore[arg-type]
                title=change.title,
                why_it_matters=reason,
                importance=round(value, 2),
                facts=facts_for(change, company, candidate),
                simulated=simulated,
            )
            self.store.add_alert(alert)
            await self._deliver(alert)
            delivered.append(alert)
        # Keep the old snapshot while an alert waits for the daily cap: the next run diffs
        # again, sends what is left, and skips what was already sent (alert ids repeat).
        if not simulated and not deferred:
            self.store.save_snapshot(candidate.entity_id, new, now)
        return delivered

    async def _deliver(self, alert: Alert) -> None:
        if self.publish is None:
            return
        result = self.publish("alert", alert.model_dump(mode="json"))
        if inspect.isawaitable(result):
            await result


def facts_for(change: Change, company: dict[str, Any], candidate: Candidate) -> list[Fact]:
    if change.kind == "new_round":
        round_ = next((r for r in candidate.rounds if r.entity_id == change.key), None)
        return [round_.amount, round_.date] if round_ else []
    if change.kind == "executive_change":
        rel, person_id = change.key.split(":")[:2]
        # The last edge for a person wins, as in the snapshot (a staged patch appends one).
        edges = [e for e in relationships(company, "incoming", rel) if e["id"] == person_id]
        edge = edges[-1] if edges else None
        if edge is None or rel not in EXECUTIVE_EDGES:
            return []
        return [edge_fact(edge, "valid_until" if change.data.get("left") else "valid_since")]
    if change.kind == "headcount_jump":
        return [candidate.headcount]
    if change.kind == "acquisition":
        edges = relationships(company, "outgoing", "PARTICIPATES_IN_CORPORATE_EVENT")
        edge = next((e for e in edges if e["id"] == change.key), None)
        return [edge_fact(edge, "event_date")] if edge else []
    if change.kind == "status_change":
        return [property_fact(company, "operational_status")]
    return []


def merge(base: Any, patch: Any) -> Any:
    """Dicts merge key by key; lists in the patch are appended (a later edge for the same
    neighbour wins in the snapshot, e.g. an executive edge that now has `valid_until`)."""
    if isinstance(base, dict) and isinstance(patch, dict):
        out = copy.deepcopy(base)
        for key, value in patch.items():
            out[key] = merge(out.get(key), value) if key in out else copy.deepcopy(value)
        return out
    if isinstance(base, list) and isinstance(patch, list):
        return copy.deepcopy(base) + copy.deepcopy(patch)
    return copy.deepcopy(patch)


def _alert_id(entity_id: str, change: Change, salt: str) -> str:
    raw = f"{entity_id}|{change.kind}|{change.key}|{salt}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
