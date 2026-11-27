"""Replaying background replies built with background_reply(), without Firefox."""

import json

from auto_fxui.classes.recording import (
    CHAT_PATH,
    Recording,
    background_reply,
    summarize_request,
)


def request(purpose: str, schema: str | None = None) -> dict:
    """Summarize a background request the way MockServer does."""
    body = {
        "model": "m",
        "stream": False,
        "messages": [{"role": "user", "content": "x"}],
    }
    if schema:
        body["response_format"] = {"json_schema": {"name": schema}}
    return summarize_request(CHAT_PATH, {"purpose": purpose}, body)


def reply_text(response: dict) -> str:
    return response["body"]["choices"][0]["message"]["content"]


def test_builds_a_non_streamed_reply():
    built = background_reply("monitor", {"conditionMet": False})
    assert built["request"] == {
        "path": CHAT_PATH,
        "purpose": "monitor",
        "stream": False,
    }
    assert built["response"]["status"] == 200
    assert json.loads(reply_text(built["response"])) == {"conditionMet": False}


def test_replay_matches_by_purpose():
    recording = Recording([background_reply("monitor", "watching")])
    assert reply_text(recording.match(request("monitor"))) == "watching"
    assert recording.match(request("aitab")) is None


def test_replay_matches_by_schema_within_a_purpose():
    classify = "SmartFormFillFieldClassification"
    values = "SmartFormFillFormValues"
    recording = Recording(
        [
            background_reply("smart-form-fill", "any"),
            background_reply("smart-form-fill", "classify", schema=classify),
            background_reply("smart-form-fill", "values", schema=values),
        ]
    )
    assert (
        reply_text(recording.match(request("smart-form-fill", classify))) == "classify"
    )
    assert reply_text(recording.match(request("smart-form-fill", values))) == "values"
    # A reply built without a schema answers the purpose's other requests.
    other = request("smart-form-fill", "SmartFormFillRelevantTabs")
    assert reply_text(recording.match(other)) == "any"
