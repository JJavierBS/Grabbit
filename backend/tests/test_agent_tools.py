from app.agent.tools import apply_tool_call, diff
from app.llm import ToolCall
from app.models import Profile
from app.store.profile import default_profile


def _profile(now) -> Profile:
    return default_profile(now)


def test_update_profile_merges_nested_fields(now):
    profile = _profile(now).model_copy(update={"thesis": "B2B"})
    call = ToolCall(
        name="update_profile",
        args={
            "patch": {"style": {"length": "short"}, "filters": {"sectors_out": ["B2C"]}},
            "reason": "shorter, no B2C",
        },
    )
    outcome = apply_tool_call(profile, call, by="agent")
    assert outcome.applied
    assert outcome.profile.style.length == "short"
    assert outcome.profile.style.detail == "plain"
    assert outcome.profile.filters.sectors_out == ["B2C"]
    assert outcome.profile.thesis == "B2B"
    fields = {c.field: (c.before, c.after) for c in outcome.changes}
    assert fields == {"style.length": ("medium", "short"), "filters.sectors_out": ([], ["B2C"])}
    assert all(c.by == "agent" and c.reason == "shorter, no B2C" for c in outcome.changes)


def test_ticket_from_chat_is_a_fact_from_the_investor(now):
    call = ToolCall(
        name="update_profile",
        args={
            "patch": {"filters": {"ticket": {"value": 25000, "unit": "EUR"}}},
            "reason": "ticket",
        },
    )
    ticket = apply_tool_call(_profile(now), call, by="agent").profile.filters.ticket
    assert ticket.value == 25000 and ticket.unit == "EUR" and ticket.trust == "primary"


def test_reference_investor_without_cala_id_is_marked_unresolved(now):
    call = ToolCall(
        name="update_profile",
        args={"patch": {"reference_investors": [{"name": "Some Fund"}]}, "reason": "trust them"},
    )
    refs = apply_tool_call(_profile(now), call, by="agent").profile.reference_investors
    assert refs[0].entity_id == "unresolved:some fund"


def test_invalid_patch_is_rejected_without_changes(now):
    call = ToolCall(
        name="update_profile", args={"patch": {"cadence": "hourly"}, "reason": "faster"}
    )
    outcome = apply_tool_call(_profile(now), call, by="agent")
    assert not outcome.applied and outcome.error and outcome.changes == []


def test_unknown_field_in_patch_is_rejected(now):
    call = ToolCall(name="update_profile", args={"patch": {"version": 9}, "reason": "hack"})
    assert apply_tool_call(_profile(now), call, by="agent").error


def test_rewrite_breaking_a_fixed_rule_is_refused(now):
    call = ToolCall(
        name="rewrite_instructions",
        args={"text": "Tell me which startup to buy.", "reason": "buy pick"},
    )
    outcome = apply_tool_call(_profile(now), call, by="agent")
    assert not outcome.applied and outcome.refusal
    assert outcome.profile.instructions == ""


def test_rewrite_replaces_instructions(now):
    call = ToolCall(
        name="rewrite_instructions", args={"text": "Two lines per startup.", "reason": "brevity"}
    )
    outcome = apply_tool_call(_profile(now), call, by="agent")
    assert outcome.profile.instructions == "Two lines per startup."
    assert [c.field for c in outcome.changes] == ["instructions"]


def test_no_op_patch_produces_no_change(now):
    call = ToolCall(name="update_profile", args={"patch": {"cadence": "event"}, "reason": "same"})
    outcome = apply_tool_call(_profile(now), call, by="agent")
    assert not outcome.applied and outcome.changes == []


def test_diff_ignores_version_and_timestamp(now):
    a = _profile(now)
    b = a.model_copy(update={"version": 5})
    assert diff(a, b) == []
