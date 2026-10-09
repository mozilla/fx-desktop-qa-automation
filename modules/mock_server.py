import json
import logging
import re
import threading

import requests
from pytest_httpserver import HTTPServer
from werkzeug.wrappers import Request, Response

from modules.classes.recording import (
    SEARCH_PATH,
    Recording,
    is_chat_message,
    streamed_text,
    streamed_tool_calls,
    summarize_request,
)

# Stage MLPA, the LLM proxy behind Smart Window. It accepts prod FxA tokens
# only, the same as Firefox's own eval tooling (toolkit/components/ml/eval).
MLPA_STAGE_URL = "https://mlpa-nonprod-stage-mozilla.freetls.fastly.net/v1"

# Not forwarded upstream: hop-by-hop headers, and Authorization, which is
# replaced with the real token.
DROPPED_HEADERS = {
    "authorization",
    "connection",
    "content-length",
    "host",
    "accept-encoding",
}


class MockServer:
    """
    Local stand-in for the Smart Window LLM and web search endpoints.

    Firefox is pointed here with the browser.smartwindow.endpoint and
    browser.smartwindow.searchQuery.endpointURL prefs. Modes:

    - replay: serve responses from a Recording
    - record: forward to MLPA with a real token and add the responses to the
      Recording
    - live: forward to MLPA without recording

    Threaded, so a streaming chat reply doesn't block the background requests
    Firefox sends alongside it. Port 0 gives each xdist worker its own port.
    """

    def __init__(self):
        self.server = HTTPServer(host="127.0.0.1", port=0, threaded=True)
        self.server.expect_request(re.compile("^/v1/")).respond_with_handler(
            self._handle
        )
        self._lock = threading.Lock()
        self._idle = threading.Condition(self._lock)
        self._in_flight = 0
        self.reset()

    def start(self) -> "MockServer":
        self.server.start()
        return self

    def stop(self):
        if self.server.is_running():
            self.server.stop()

    @property
    def endpoint_url(self) -> str:
        """Value for browser.smartwindow.endpoint"""
        return self.server.url_for("/v1")

    @property
    def search_url(self) -> str:
        """Value for browser.smartwindow.searchQuery.endpointURL"""
        return self.server.url_for(SEARCH_PATH)

    def reset(
        self,
        recording: Recording | None = None,
        mode: str = "replay",
        upstream: str | None = None,
        token: str | None = None,
    ):
        """
        Start serving a new test. With no arguments every request goes
        unanswered, which is the state between tests.
        """
        with self._lock:
            self.recording = recording or Recording()
            self.mode = mode
            self.upstream = upstream
            self.token = token
            # Every request and the response it got (None if unanswered).
            self.served = []
            self.unmatched = []
            self.upstream_errors = []
        self.server.clear_log()

    def wait_until_idle(self, timeout: float = 30) -> bool:
        """
        Wait for forwarded requests to finish, so a recording isn't saved
        while a reply is still streaming in. Returns False on timeout.
        """
        with self._idle:
            return self._idle.wait_for(lambda: self._in_flight == 0, timeout)

    def chat_reply_text(self, prompt: str) -> str:
        """
        Return the text of the newest chat reply served for `prompt`, with
        whitespace collapsed.

        Waits for forwarded replies to finish streaming first, so it gives the
        whole reply in record and live modes too.

        Raises
        ------
        AssertionError
            If no chat reply with text was served for `prompt`.
        """
        for request, response in reversed(self._chat_responses()):
            text = streamed_text(response)
            if request.get("last_user_message") == prompt and text:
                return " ".join(text.split())
        raise AssertionError(f"No chat reply was served for {prompt!r}")

    def tool_calls(self, name: str) -> list[dict]:
        """
        Return the arguments of each call to tool `name` in the chat replies
        served, oldest first. This is what the model asked Firefox to do.

        Waits for forwarded replies to finish streaming first.
        """
        return [
            call["arguments"]
            for _, response in self._chat_responses()
            for call in streamed_tool_calls(response)
            if call["name"] == name
        ]

    def _chat_responses(self) -> list[tuple[dict, dict]]:
        """(request, response) for each streamed chat reply served, oldest first."""
        self.wait_until_idle()
        with self._lock:
            served = list(self.served)
        return [
            (i["request"], i["response"])
            for i in served
            if is_chat_message(i["request"])
            and i["response"]
            and "events" in i["response"]
        ]

    def _handle(self, request: Request) -> Response:
        body = request.get_json(silent=True) or {}
        summary = summarize_request(request.path, request.headers, body)
        with self._lock:
            mode = self.mode
        if mode == "replay":
            return self._replay(summary)
        with self._lock:
            self._in_flight += 1
        try:
            return self._forward(request, summary, record=mode == "record")
        except BaseException:
            self._done()
            raise

    def _replay(self, summary: dict) -> Response:
        with self._lock:
            response = self.recording.match(summary)
            self.served.append({"request": summary, "response": response})
        if response is not None:
            return _to_response(response)
        if summary["path"] == SEARCH_PATH or is_chat_message(summary):
            with self._lock:
                self.unmatched.append(summary)
            logging.warning(f"Mock server has no recording for {summary}")
            return Response(
                json.dumps({"error": "no recording for this request"}),
                status=500,
                content_type="application/json",
            )
        # Background features (title generation, conversation starters...)
        # give up quietly on an error, so they don't need recordings.
        logging.info(f"Mock server is not answering {summary}")
        return Response(status=503)

    def _forward(self, request: Request, summary: dict, record: bool) -> Response:
        headers = {
            k: v for k, v in request.headers.items() if k.lower() not in DROPPED_HEADERS
        }
        headers["Authorization"] = f"Bearer {self.token}"
        url = self.upstream + request.path.removeprefix("/v1")
        upstream = requests.post(
            url, data=request.get_data(), headers=headers, stream=True, timeout=60
        )
        content_type = upstream.headers.get("content-type", "")

        if not upstream.ok:
            # Not recorded: a bad token or a server error is not a reply worth
            # replaying.
            with self._lock:
                self.served.append({"request": summary, "response": None})
                self.upstream_errors.append((upstream.status_code, summary))
            self._done()
            return Response(
                upstream.content, status=upstream.status_code, content_type=content_type
            )

        if content_type.startswith("text/event-stream"):

            def relay():
                raw = b""
                try:
                    for chunk in upstream.iter_content(chunk_size=None):
                        raw += chunk
                        yield chunk
                    response = {
                        "status": upstream.status_code,
                        "events": _parse_sse(raw),
                    }
                    self._served(summary, response, record)
                finally:
                    self._done()

            return Response(relay(), content_type=content_type)

        response = {"status": upstream.status_code, "body": upstream.json()}
        self._served(summary, response, record)
        self._done()
        return Response(
            upstream.content, status=upstream.status_code, content_type=content_type
        )

    def _served(self, summary: dict, response: dict, record: bool):
        interaction = {"request": summary, "response": response}
        with self._lock:
            self.served.append(interaction)
            if record:
                self.recording.add(interaction)

    def _done(self):
        with self._idle:
            self._in_flight -= 1
            self._idle.notify_all()


def _to_response(response: dict) -> Response:
    if "events" in response:

        def stream():
            for event in response["events"]:
                yield f"data: {json.dumps(event)}\n\n"
            yield "data: [DONE]\n\n"

        return Response(
            stream(), status=response["status"], content_type="text/event-stream"
        )
    return Response(
        json.dumps(response["body"]),
        status=response["status"],
        content_type="application/json",
    )


def _parse_sse(raw: bytes) -> list[dict]:
    events = []
    for line in raw.decode().splitlines():
        if not line.startswith("data:"):
            continue
        data = line.removeprefix("data:").strip()
        if data and data != "[DONE]":
            events.append(json.loads(data))
    return events
