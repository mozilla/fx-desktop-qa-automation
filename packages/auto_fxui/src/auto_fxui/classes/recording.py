import copy
import json
from pathlib import Path

CHAT_PATH = "/v1/chat/completions"
SEARCH_PATH = "/v1/search"

# Fields of each response chunk that change on every call. Left out of saved
# recordings so a re-record's diff shows only real changes.
VOLATILE_FIELDS = ("id", "created", "system_fingerprint", "usage")

# Extras the LLM proxy adds to messages and tool calls (Gemini's thought
# signatures, which also change on every call). Firefox doesn't read them.
PROVIDER_FIELDS = "provider_specific_fields"


def summarize_request(path: str, headers, body: dict) -> dict:
    """
    Reduce a Smart Window request to the fields that are recorded and matched.

    Only the fields below are copied, so tokens, page content and the system
    prompt never reach a recording. Background requests have no prompt: theirs
    embeds page content.

    Parameters
    ----------
    path : str
        Request path, e.g. "/v1/chat/completions".
    headers : Mapping
        Request headers (case-insensitive, as werkzeug provides them).
    body : dict
        Parsed JSON request body.
    """
    if path == SEARCH_PATH:
        return {"path": path, "query": body.get("query")}
    summary = {
        "path": path,
        "purpose": headers.get("purpose"),
        "model": body.get("model"),
        "stream": bool(body.get("stream")),
    }
    if is_chat_message(summary):
        messages = body.get("messages") or []
        user_messages = [m for m in messages if m.get("role") == "user"]
        summary["last_user_message"] = (
            _message_text(user_messages[-1]) if user_messages else None
        )
        summary["tool_results"] = sum(1 for m in messages if m.get("role") == "tool")
    return summary


def is_chat_message(request: dict) -> bool:
    """
    True for a request answering a message the user sent: Firefox streams
    those, with purpose "chat". Background requests aren't streamed, though
    some Firefox versions also send them with purpose "chat".
    """
    return (
        request["path"] == CHAT_PATH
        and request.get("purpose") == "chat"
        and bool(request.get("stream"))
    )


def match_key(request: dict) -> tuple:
    """
    Return the fields a replayed request must share with a recorded one.

    The model is left out so a model swap on the server side does not
    invalidate every recording.
    """
    if request["path"] == SEARCH_PATH:
        return (request["path"], request.get("query"))
    if not is_chat_message(request):
        return (request["path"], request.get("purpose"))
    return (
        request["path"],
        request.get("purpose"),
        request.get("last_user_message"),
        request.get("tool_results", 0),
    )


def _message_text(message: dict) -> str:
    content = message.get("content")
    if isinstance(content, list):
        return "".join(part.get("text", "") for part in content)
    return content or ""


def streamed_text(response: dict) -> str:
    """Return the assistant text a streamed response sent, chunks joined."""
    return "".join(delta.get("content") or "" for delta in _streamed_deltas(response))


def streamed_tool_calls(response: dict) -> list[dict]:
    """
    Return the tool calls in a streamed response, each as {name, arguments}.
    Arguments arrive in pieces across chunks and are joined here.
    """
    calls = {}
    for delta in _streamed_deltas(response):
        for part in delta.get("tool_calls") or []:
            call = calls.setdefault(part.get("index", 0), {"name": "", "arguments": ""})
            function = part.get("function") or {}
            call["name"] += function.get("name") or ""
            call["arguments"] += function.get("arguments") or ""
    return [
        {"name": call["name"], "arguments": json.loads(call["arguments"] or "{}")}
        for _, call in sorted(calls.items())
    ]


def _without_volatile_fields(response: dict) -> dict:
    """
    Return a copy of `response` without VOLATILE_FIELDS or PROVIDER_FIELDS.
    """
    response = copy.deepcopy(response)
    parts = response.get("events", []) + (
        [response["body"]] if "body" in response else []
    )
    for part in parts:
        for field in VOLATILE_FIELDS:
            part.pop(field, None)
        for choice in part.get("choices", []):
            choice.pop(PROVIDER_FIELDS, None)
            for message in (choice.get("delta"), choice.get("message")):
                if not message:
                    continue
                message.pop(PROVIDER_FIELDS, None)
                for call in message.get("tool_calls") or []:
                    call.pop(PROVIDER_FIELDS, None)
    return response


def _streamed_deltas(response: dict) -> list[dict]:
    return [
        choice.get("delta") or {}
        for event in response.get("events", [])
        for choice in event.get("choices", [])
    ]


class Recording:
    """
    Recorded responses for one test, stored as JSON under data/recordings/.

    Each interaction pairs a request summary (see summarize_request) with the
    response to send back: `events` for a streamed (SSE) reply, `body` for a
    JSON one.
    """

    def __init__(
        self, interactions: list[dict] | None = None, meta: dict | None = None
    ):
        self.interactions = interactions or []
        self.meta = meta or {}
        self._served = {}

    @classmethod
    def load(cls, path: Path) -> "Recording":
        """Load a recording, or return an empty one if the file doesn't exist."""
        if not path.exists():
            return cls()
        data = json.loads(path.read_text())
        return cls(data["interactions"], data.get("meta"))

    def save(self, path: Path):
        """Write the recording, without VOLATILE_FIELDS or PROVIDER_FIELDS."""
        path.parent.mkdir(parents=True, exist_ok=True)
        interactions = [
            {**i, "response": _without_volatile_fields(i["response"])}
            for i in self.interactions
        ]
        data = {"meta": self.meta, "interactions": interactions}
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    def add(self, interaction: dict):
        self.interactions.append(interaction)

    def match(self, request: dict) -> dict | None:
        """
        Return the recorded response for `request`, or None if there is none.

        Responses with the same key (a tool call and its follow-up) are served
        in recorded order, then the last one repeats.
        """
        key = match_key(request)
        candidates = [i for i in self.interactions if match_key(i["request"]) == key]
        if not candidates:
            return None
        served = self._served.get(key, 0)
        self._served[key] = served + 1
        return candidates[min(served, len(candidates) - 1)]["response"]


# Builders for hand-written replies. They produce the same structure a
# recording does, so tests can use them where the reply text is all that
# matters and a recording would add nothing.


def chat_reply(prompt: str, text: str, tool_results: int = 0) -> dict:
    """
    A streamed assistant reply of `text` to `prompt`, one word per chunk.

    Set `tool_results` to the number of tool results already sent back when
    this is the reply that follows a tool_call().
    """
    words = text.split(" ")
    events = [
        _chunk({"content": word if i == 0 else f" {word}"})
        for i, word in enumerate(words)
    ]
    events.append(_chunk({}, finish_reason="stop"))
    return {
        "request": {
            "path": CHAT_PATH,
            "purpose": "chat",
            "stream": True,
            "last_user_message": prompt,
            "tool_results": tool_results,
        },
        "response": {"status": 200, "events": events},
    }


def tool_call(prompt: str, name: str, arguments: dict, tool_results: int = 0) -> dict:
    """A streamed reply to `prompt` that asks Firefox to run tool `name`."""
    call = {
        "index": 0,
        "id": f"call_{tool_results + 1}",
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(arguments)},
    }
    return {
        "request": {
            "path": CHAT_PATH,
            "purpose": "chat",
            "stream": True,
            "last_user_message": prompt,
            "tool_results": tool_results,
        },
        "response": {
            "status": 200,
            "events": [
                _chunk({"tool_calls": [call]}),
                _chunk({}, finish_reason="tool_calls"),
            ],
        },
    }


def search_results(query: str, results: list[dict]) -> dict:
    """
    A web search response for `query`.

    `results` items take the keys Firefox reads: title, url, text and
    optionally publishedDate.
    """
    return {
        "request": {"path": SEARCH_PATH, "query": query},
        "response": {"status": 200, "body": {"results": results}},
    }


def _chunk(delta: dict, finish_reason: str | None = None) -> dict:
    return {
        "object": "chat.completion.chunk",
        "choices": [{"index": 0, "delta": delta, "finish_reason": finish_reason}],
    }
