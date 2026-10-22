import datetime
from os import environ
from pathlib import Path

import pytest
from pytest_httpserver import HTTPServer

from modules.browser_object import SmartWindow, SmartWindowChat
from modules.classes.recording import Recording
from modules.mock_server import MLPA_STAGE_URL, MockServer
from modules.taskcluster import get_tc_secret

TAB_PAGES = Path("data", "smart_window_pages")


@pytest.fixture()
def suite_id():
    return ("S70279", "Smart Window")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict, mock_server_session: MockServer):
    """
    Smart Window ships disabled by default; every test in this suite needs the
    feature available before the window opens.

    First-run onboarding is marked complete with a model chosen, so a Smart
    Window opens straight to its normal view. Tests of sign-up or onboarding
    override add_to_prefs_list to reset these two prefs.

    With first run complete, Firefox opens the AI sidebar whenever a window
    becomes Smart; openByDefault is turned off so a newly activated Smart
    Window starts with the sidebar closed.

    LLM and web search requests go to the mock server, never to MLPA. The
    ML engine that sends them is off under automation unless browser.ml.enable
    is set.
    """
    prefs = [
        ("browser.smartwindow.enabled", True),
        ("browser.smartwindow.firstrun.hasCompleted", True),
        # Choice id "1" (Gemini today). Set before launch, so it can't be
        # picked by name like SmartWindowFirstRun.select_model does.
        ("browser.smartwindow.firstrun.modelChoice", "1"),
        ("browser.smartwindow.sidebar.openByDefault", False),
        ("browser.ml.enable", True),
        ("browser.smartwindow.endpoint", mock_server_session.endpoint_url),
        (
            "browser.smartwindow.searchQuery.endpointURL",
            mock_server_session.search_url,
        ),
    ]
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []


@pytest.fixture()
def smart_window(driver):
    """Provide the Smart Window BOM for a window still in the Classic state."""
    return SmartWindow(driver)


@pytest.fixture()
def fxa_env():
    # On Taskcluster, read the secret at the task's own level (PRs: 1, main/cron: 3)
    level = environ.get("MOZ_SCM_LEVEL")
    if level:
        fxa_keys = get_tc_secret("ci_waf_token", level=int(level))
        if fxa_keys and fxa_keys.get("stage"):
            environ["CI_WAF_TOKEN"] = fxa_keys["stage"]
    return "stage"


@pytest.fixture()
def active_smart_window(driver):
    """
    Provide the Smart Window BOM with the window already in the Smart Window
    state, for tests about behaviour *inside* a Smart Window.

    See SmartWindow.activate_smart_window for why this does not go through the
    product's own (FxA-gated) entry points.
    """
    sw = SmartWindow(driver)
    sw.activate_smart_window()
    return sw


@pytest.fixture(scope="session")
def mock_server_session():
    """The mock server, started once per worker. Tests use mock_server."""
    server = MockServer().start()
    yield server
    server.stop()


@pytest.fixture()
def mock_server(mock_server_session: MockServer, opt_mock_mode: str, request):
    """
    Point the mock server at this test's recording, in the --mock-mode given.

    See recording_path for where the recording lives. Replay fails the test
    if Firefox sent a chat or search request that isn't recorded. Record and
    live forward to stage MLPA with the prod FxA token in
    MOZ_FXA_BEARER_TOKEN; record then saves the recording.
    """
    path = recording_path(request.node)
    if opt_mock_mode == "replay":
        mock_server_session.reset(Recording.load(path))
    else:
        token = environ.get("MOZ_FXA_BEARER_TOKEN")
        if not token:
            pytest.fail(
                f"--mock-mode={opt_mock_mode} needs a prod FxA token in "
                "MOZ_FXA_BEARER_TOKEN (see SMART_WINDOW_MOCK_SERVER.md)"
            )
        recording = Recording(
            meta={
                "upstream": MLPA_STAGE_URL,
                "firefox_version": request.getfixturevalue("version"),
                "recorded_at": datetime.date.today().isoformat(),
            }
        )
        mock_server_session.reset(recording, opt_mock_mode, MLPA_STAGE_URL, token)

    yield mock_server_session

    server = mock_server_session
    server.wait_until_idle()
    unmatched, upstream_errors = server.unmatched, server.upstream_errors
    if opt_mock_mode == "record" and not upstream_errors:
        server.recording.save(path)
    server.reset()
    if unmatched:
        missing = sorted(
            {u.get("last_user_message") or u.get("query") for u in unmatched}
        )
        problem = (
            f"{path} has no recording for: {missing}"
            if path.exists()
            else f"This test has no recording yet ({path} doesn't exist)"
        )
        pytest.fail(
            f"{problem}. Record it with a prod FxA token in "
            "MOZ_FXA_BEARER_TOKEN (see SMART_WINDOW_MOCK_SERVER.md):\n"
            f'  pytest "{request.node.nodeid}" --mock-mode=record'
        )
    if upstream_errors:
        pytest.fail(
            f"MLPA returned errors: {upstream_errors}. A 401 means "
            "MOZ_FXA_BEARER_TOKEN is missing, expired or not a prod token."
        )


@pytest.fixture()
def smart_window_chat(
    active_smart_window: SmartWindow, mock_server: MockServer, driver
) -> SmartWindowChat:
    """
    Provide the chat BOM ready to chat: Smart Window active, replies from the
    mock server, and a stand-in FxA token so Firefox sends requests without
    being signed in.
    """
    active_smart_window.stub_fxa_token()
    return SmartWindowChat(driver)


def recording_path(node: pytest.Item) -> Path:
    """
    Return where a test's recording lives:
    data/recordings/<suite>/<test file name>.json, or
    data/recordings/<suite>/<test file name>/<parameter id>.json for each case
    of a parametrized test, since its cases send different requests.
    """
    folder = Path("data", "recordings", node.path.parent.name)
    callspec = getattr(node, "callspec", None)
    if callspec:
        return folder / node.path.stem / f"{callspec.id}.json"
    return folder / f"{node.path.stem}.json"


@pytest.fixture(scope="session")
def tab_pages_server():
    """
    Serve the pages in data/smart_window_pages/ on localhost, once per worker.

    Its own server rather than pytest-httpserver's shared one: that server
    is created once per worker by whichever suite asks first, and the address
    bar suite pins it to 127.0.0.1. The host is part of each tab's URL token,
    so on 127.0.0.1 the tokens no longer match the recordings.
    """
    server = HTTPServer(host="localhost", port=0)
    for page in TAB_PAGES.glob("*.html"):
        server.expect_request(f"/{page.name}").respond_with_data(
            page.read_text(), content_type="text/html"
        )
    server.start()
    yield server
    server.clear()
    server.stop()


@pytest.fixture()
def tab_pages(tab_pages_server: HTTPServer):
    """
    Return a function that turns page file names in data/smart_window_pages/
    into their URLs.

    The pages are served from localhost on a random port. Smart Window's URL
    tokens are built from host and path only, so recordings don't depend on
    the port.
    """
    return lambda names: [tab_pages_server.url_for(f"/{name}") for name in names]
