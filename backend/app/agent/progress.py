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


# One event per this many attendees: the label changes visibly, the stream stays light.
COUNT_EVERY = 5


def report_phase(phase: TurnPhase) -> None:
    events.publish("progress", TurnProgress(phase=phase, label=LABELS[phase]))


def report_attendees(checked: int, total: int, startups: int) -> None:
    """The Slush walk, counted: attendees checked so far and the startups among them."""
    if checked % COUNT_EVERY and checked not in (1, total):
        return
    found = f" · {startups} startup{'' if startups == 1 else 's'} so far" if startups else ""
    events.publish(
        "progress",
        TurnProgress(
            phase="cala",
            label=f"Checking Slush attendees in Cala: {checked} of {total}{found}…",
            done=checked,
            total=total,
        ),
    )
