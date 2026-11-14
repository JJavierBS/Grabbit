from app.models import ProfileChange
from app.store import profile as store


def _change(version, field="cadence", before="event", after="daily"):
    return ProfileChange(
        version=version, field=field, before=before, after=after, reason="r", by="agent"
    )


def test_first_read_creates_version_one(now):
    assert store.current(now).version == 1
    assert store.history() == []


def test_save_version_increments_and_records_history(now):
    p1 = store.current(now)
    p2 = store.save_version(p1.model_copy(update={"cadence": "daily"}), [_change(2)], now)
    assert p2.version == 2 and store.current().cadence == "daily"
    p3 = store.save_version(
        p2.model_copy(update={"thesis": "x"}), [_change(3, "thesis", "", "x")], now
    )
    assert [c.version for c in store.history()] == [3, 2]
    assert p3.version == 3


def test_undo_restores_previous_version_and_drops_its_changes(now):
    p1 = store.current(now)
    store.save_version(p1.model_copy(update={"cadence": "daily"}), [_change(2)], now)
    restored = store.undo()
    assert restored.version == 1 and restored.cadence == "event"
    assert store.history() == []


def test_undo_with_nothing_to_undo_returns_none(now):
    store.current(now)
    assert store.undo() is None
