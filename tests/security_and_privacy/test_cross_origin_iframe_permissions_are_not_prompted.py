import time

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.remote.webelement import WebElement

from modules.browser_object import Navigation
from modules.page_object import GenericPage

TEST_URL = "https://joo.uber.space/frame-permissions.html"

# The frame under test is embedded with
# allow="geolocation https://permission.site; camera https://permission.site;
#        microphone https://permission.site"
# but loads joo.uber.space, so its own origin is absent from every allowlist.
# Those three features are therefore disabled in the frame and none of the
# requests below may reach the user as a doorhanger.
IFRAME_HEADING = (
    "This site cross-origin with FP allowed only for https://permission.site"
)
FRAME_ALLOW = (
    "geolocation https://permission.site; camera https://permission.site; "
    "microphone https://permission.site"
)

# Only the features named in the allow attribute are delegated away from the
# frame. Screen sharing and speaker selection keep their default "self"
# allowlist and are still expected to prompt, so they are out of scope here.
PERMISSION_BUTTONS = [
    "geolocation-button",
    "camera-button",
    "microphone-button",
    "camera-and-microphone-button",
]

# Some of the requests are delayed by the page, so give any doorhanger enough
# time to animate in before declaring that none was raised.
PROMPT_GRACE_PERIOD = 3


@pytest.fixture()
def test_case():
    return "602563"


@pytest.fixture()
def add_to_prefs_list():
    """Serve fake camera and microphone streams so no real hardware is needed."""
    return [("media.navigator.streams.fake", True)]


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
    """
    Return the frame sitting under IFRAME_HEADING, not the first frame on the page.

    The page embeds 15 frames and the unlabelled first one delegates geolocation
    back to joo.uber.space, so picking it up by accident would invert the test.
    Pin the match down by count and by the attributes that make this frame the
    one under test.
    """
    page.switch_to_default_frame()
    frames = page.get_element("cross-origin-iframe", multiple=True)
    assert len(frames) == 1, (
        f"Expected one frame under {IFRAME_HEADING!r}, got {len(frames)}"
    )

    frame = frames[0]
    assert frame.get_attribute("src") == TEST_URL, (
        f"Frame under test should load {TEST_URL}, got {frame.get_attribute('src')}"
    )
    assert frame.get_attribute("allow") == FRAME_ALLOW, (
        f"Frame under test should delegate only to https://permission.site, "
        f"got {frame.get_attribute('allow')!r}"
    )
    return frame


def click_in_cross_origin_iframe(page: GenericPage, button: str) -> None:
    """Scroll the frame under test into view, then ask for a permission from it."""
    frame = locate_frame_under_test(page)
    page.scroll_to_element(frame)
    page.switch_to_iframe_context(frame)
    page.click_on(button)
    page.switch_to_default_frame()


def expect_no_permission_prompt(nav: Navigation, requested: str) -> None:
    """Assert that asking for `requested` did not raise a doorhanger."""
    time.sleep(PROMPT_GRACE_PERIOD)
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
    C602563 - This site cross-origin with FP allowed only for https://permission.site
    """

    # Open the Firefox browser and reach: https://joo.uber.space/frame-permissions.html
    page = GenericPage(driver, url=TEST_URL).open()
    page.elements |= temp_selectors

    for button in PERMISSION_BUTTONS:
        # Scroll and find the iframe whose permissions policy delegates
        # geolocation, camera and microphone only to https://permission.site,
        # then request each of those features from it
        click_in_cross_origin_iframe(page, button)

        # No permission prompts are displayed
        expect_no_permission_prompt(nav, button)
