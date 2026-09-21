import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.remote.webelement import WebElement

from modules.browser_object import Navigation
from modules.page_object import GenericPage

TEST_URL = "https://joo.uber.space/frame-permissions.html"

# Frame loads joo.uber.space but delegates only to permission.site, so all
# three features are disabled and must never prompt.
IFRAME_HEADING = (
    "This site cross-origin with FP allowed only for https://permission.site"
)
FRAME_ALLOW = (
    "geolocation https://permission.site; camera https://permission.site; "
    "microphone https://permission.site"
)

# Each button with the request it fires. Screen and speaker keep their default
# "self" allowlist, so they are excluded.
PERMISSION_REQUESTS = [
    ("geolocation-button", "geolocation"),
    ("camera-button", '{"video": true}'),
    ("microphone-button", '{"audio": true}'),
    ("camera-and-microphone-button", '{"audio": true, "video": true}'),
]

# Blocked rejects at once; prompting stays pending until the script times out.
REQUEST_SCRIPT = """
const done = arguments[arguments.length - 1];
const request = arguments[0];
if (request === "geolocation") {
  navigator.geolocation.getCurrentPosition(
    () => done("granted"),
    e => done(e.code === 1 ? "denied" : "failed: code " + e.code),
  );
} else {
  navigator.mediaDevices
    .getUserMedia(JSON.parse(request))
    .then(() => done("granted"))
    .catch(e => done(e.name === "NotAllowedError" ? "denied" : "failed: " + e.name));
}
"""

SCRIPT_TIMEOUT = 10


@pytest.fixture()
def test_case():
    return "602563"


@pytest.fixture()
def add_to_prefs_list():
    """Serve fake camera and microphone streams so no real hardware is needed."""
    return [("media.navigator.streams.fake", True)]


@pytest.fixture(autouse=True)
def script_timeout(driver: Firefox):
    """Bound the pending-doorhanger case, restoring the default even on failure."""
    original = driver.timeouts.script
    driver.set_script_timeout(SCRIPT_TIMEOUT)
    yield
    driver.set_script_timeout(original)


@pytest.fixture()
def temp_selectors():
    return {
        "cross-origin-iframe": {
            "selectorData": f'//h2[text()="{IFRAME_HEADING}"]/following-sibling::iframe',
            "strategy": "xpath",
            "groups": ["doNotCache"],
        },
        "geolocation-button": {
            "selectorData": "geo",
            "strategy": "id",
            "groups": ["doNotCache"],
        },
        "camera-button": {
            "selectorData": "webRTC-shareDevices",
            "strategy": "id",
            "groups": ["doNotCache"],
        },
        "microphone-button": {
            "selectorData": "webRTC-shareMicrophone",
            "strategy": "id",
            "groups": ["doNotCache"],
        },
        "camera-and-microphone-button": {
            "selectorData": "webRTC-shareDevices2",
            "strategy": "id",
            "groups": ["doNotCache"],
        },
    }


def locate_frame_under_test(page: GenericPage) -> WebElement:
    """Return the frame under IFRAME_HEADING, not one of the other 14."""
    page.switch_to_default_frame()

    frames = page.get_element("cross-origin-iframe", multiple=True)
    assert len(frames) == 1, (
        f"Expected one frame under {IFRAME_HEADING!r}, got {len(frames)}"
    )

    # Self-embed is deliberate: matching TEST_URL is the invariant, not a
    # copy-paste. A frame pointed anywhere else is not this test case.
    frame = frames[0]
    assert frame.get_attribute("src") == TEST_URL, (
        f"Frame under test should self-embed {TEST_URL}, got {frame.get_attribute('src')}"
    )
    assert frame.get_attribute("allow") == FRAME_ALLOW, (
        f"Frame under test should delegate only to https://permission.site, "
        f"got {frame.get_attribute('allow')!r}"
    )
    return frame


def request_permission_in_frame(page: GenericPage, button: str, request: str) -> None:
    """Click `button` in the frame, then wait for `request` to be denied."""
    frame = locate_frame_under_test(page)
    page.scroll_to_element(frame)
    page.switch_to_iframe_context(frame)
    page.click_on(button)

    try:
        outcome = page.driver.execute_async_script(REQUEST_SCRIPT, request)
    except TimeoutException:
        raise AssertionError(
            f"{button}: request never settled, so it is waiting on a doorhanger"
        ) from None

    assert outcome == "denied", (
        f"{button}: expected the request to be denied by the permissions policy, got {outcome!r}"
    )
    page.switch_to_default_frame()


def expect_no_permission_prompt(nav: Navigation, requested: str) -> None:
    """Assert that asking for `requested` did not raise a doorhanger."""
    try:
        nav.element_not_visible("popup-notification")
    except TimeoutException:
        with nav.driver.context(nav.driver.CONTEXT_CHROME):
            raised = [
                prompt.get_attribute("id")
                for prompt in nav.get_elements("popup-notification")
                if prompt.is_displayed()
            ]
        raise AssertionError(
            f"Clicking {requested} raised the {raised} prompt(s) in the frame"
        ) from None


def test_cross_origin_iframe_permissions_are_not_prompted(
    driver: Firefox, nav: Navigation, temp_selectors: dict
):
    """
    C602563 - https://permission.site cross-origin iFrame
    """

    # Reach https://joo.uber.space/frame-permissions.html
    page = GenericPage(driver, url=TEST_URL).open()
    page.elements |= temp_selectors

    for button, request in PERMISSION_REQUESTS:
        # Request each delegated feature from the frame under test
        request_permission_in_frame(page, button, request)

        # No permission prompts are displayed
        expect_no_permission_prompt(nav, button)
