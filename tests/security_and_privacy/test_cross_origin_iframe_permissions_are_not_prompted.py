import time

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.remote.webelement import WebElement

from modules.browser_object import Navigation
from modules.page_object import GenericPage

TEST_URL = "https://joo.uber.space/frame-permissions.html"

# The frame loads joo.uber.space but delegates only to permission.site, so all
# three features are disabled in it and must never raise a doorhanger.
IFRAME_HEADING = (
    "This site cross-origin with FP allowed only for https://permission.site"
)
FRAME_ALLOW = (
    "geolocation https://permission.site; camera https://permission.site; "
    "microphone https://permission.site"
)

# Screen and speaker keep their default "self" allowlist and still prompt, so
# they are out of scope.
PERMISSION_BUTTONS = [
    "geolocation-button",
    "camera-button",
    "microphone-button",
    "camera-and-microphone-button",
]

# Let a delayed doorhanger animate in before declaring that none was raised.
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
    Return the frame under IFRAME_HEADING, not one of the other 14 on the page.
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
    C602563 - This sThis site cross-origin with FP allowed only for https://permission.siteite cross-origin with FP allowed only for https://permission.site
    """

    # Reach https://joo.uber.space/frame-permissions.html
    page = GenericPage(driver, url=TEST_URL).open()
    page.elements |= temp_selectors

    for button in PERMISSION_BUTTONS:
        # Request each delegated feature from the frame under test
        click_in_cross_origin_iframe(page, button)

        # No permission prompts are displayed
        expect_no_permission_prompt(nav, button)
