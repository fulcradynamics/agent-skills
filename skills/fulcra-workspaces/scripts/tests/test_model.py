import json

from fulcra_workspaces.model import (
    Authority,
    Cursor,
    Event,
    Outcome,
    State,
    parse_event,
)


def _note(**updates):
    payload = {
        "v": 1,
        "workspace": "research",
        "to": "analyst",
        "kind": "directive",
        "pri": "P1",
        "slug": "review-map",
        "ptr": "team/research/message/m-1.md",
    }
    payload.update(updates)
    return json.dumps(payload)


def test_parse_known_v1_event():
    assert parse_event(_note()) == Event(
        workspace="research",
        to="analyst",
        kind="directive",
        priority="P1",
        slug="review-map",
        ptr="team/research/message/m-1.md",
    )


def test_parse_rejects_unknown_version_kind_or_bad_pointer():
    assert parse_event(_note(v=2)) is None
    assert parse_event(_note(kind="review")) is None
    assert parse_event(_note(ptr="team/other/message/m-1.md")) is None
    assert parse_event(_note(workspace="../other")) is None


def test_parse_rejects_non_json_and_incomplete_payloads():
    assert parse_event("hello") is None
    assert parse_event("{") is None
    assert parse_event(_note(to=None)) is None
    assert parse_event(_note(slug="")) is None


def test_every_public_terminal_state_has_a_distinct_value():
    assert {state.value for state in State} == {
        "DATA",
        "CLEAR",
        "UNKNOWN",
        "BACKLOG",
        "STORE_ONLY",
        "DURABLE_ONLY",
    }


def test_outcome_json_is_deterministic():
    outcome = Outcome(
        state=State.DATA,
        message="one event",
        data={"z": 2, "a": 1},
        exit_code=0,
    )
    assert outcome.to_json() == (
        '{"data":{"a":1,"z":2},"message":"one event",'
        '"state":"DATA","type":"workspaces-result"}'
    )


def test_authority_and_cursor_are_immutable_value_objects():
    authority = Authority(
        data_type="MomentAnnotation/00000000-0000-0000-0000-000000000001",
        api_version="v1alpha1",
        protocol=1,
        base_tag="00000000-0000-0000-0000-000000000002",
        max_window_seconds=3600,
        max_records=500,
    )
    cursor = Cursor(last_read="2026-08-14T00:00:00Z", seen=("r-1",))
    assert authority.protocol == 1
    assert cursor.seen == ("r-1",)
