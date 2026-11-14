"""Tells the open chat what the current turn is doing, so the wait reads as work.

Each phase is published when the turn really enters it; nothing is timed or guessed.
"""

from app import events
from app.models import TurnPhase, TurnProgress

LABELS: dict[TurnPhase, str] = {
    "cala": "Walking the Slush attendees in Cala…",
    "llm": "Reading your message…",
    "report": "Rewriting your report…",
    "graph": "Walking Cala's graph to answer…",
}


def report_phase(phase: TurnPhase) -> None:
    events.publish("progress", TurnProgress(phase=phase, label=LABELS[phase]))
