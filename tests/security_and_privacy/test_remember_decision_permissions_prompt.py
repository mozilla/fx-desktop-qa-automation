import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import GenericPage


TEST_URL = "https://jan-ivar.github.io/dummy/iframe_iframe_gum_starcross2.html"


STREAM_IS_LIVE = """
const stream = document.getElementById("video").srcObject;
if (!stream) {
  return false;
}
const tracks = stream.getTracks();
return (
  tracks.length === 2 &&
  tracks.every((track) => track.readyState === "live")
);
"""


@pytest.fixture()
def test_case():
    return "602566"


@pytest.fixture()
def add_to_prefs_list():
    """Serve fake camera and microphone streams so no real hardware is needed."""
    return [("media.navigator.streams.fake", True)]


@pytest.fixture()
def temp_selectors():
    return {
        "gum-iframe": {
            "selectorData": "iframe#iframe1",
            "strategy": "css",
            "groups": ["doNotCache"],
        },
        "cross-iframe": {
            "selectorData": "iframe#iframe2",
            "strategy": "css",
            "groups": ["doNotCache"],
        },
        "navigate-to-landing": {
            "selectorData": "link",
            "strategy": "id",
            "groups": ["doNotCache"],
        },
        "camera-only": {
            "selectorData": 'input[type="button"][value="Camera"]',
            "strategy": "css",
            "groups": ["doNotCache"],
        },
        "gum-log": {
            "selectorData": "div#div",
            "strategy": "css",
            "groups": ["doNotCache"],
        },
    }


def enter_iframe(page: GenericPage, iframe: str) -> None:
    """Enter one of the top level iframes, starting from the main document."""
    page.switch_to_default_frame()
    page.switch_to_iframe_context(page.get_element(iframe))


def expect_camera_and_microphone_running(page: GenericPage) -> None:
    """Assert gum.html got a live A/V stream without logging an error."""
    enter_iframe(page, "gum-iframe")
    page.expect(lambda d: d.execute_script(STREAM_IS_LIVE))
    assert page.get_element("gum-log").get_attribute("innerHTML") == "", (
        "getUserMedia logged an error instead of starting the stream"
    )
    page.switch_to_default_frame()


def test_remember_decision_permissions_prompt(
    driver: Firefox, nav: Navigation, temp_selectors: dict
):
    """
    C602566 - Bug 1604813 - Remember this decision from a top level document permissions prompt does not keep the decision
    """

    page = GenericPage(driver, url=TEST_URL).open()
    page.elements |= temp_selectors

    # Check "Remember this decision" and allow the prompt raised by the top page
    nav.handle_permission_prompt(button_type="primary", remember_this_decision=True)

    # The camera and the microphone start without issues
    expect_camera_and_microphone_running(page)

    # Navigate the second iframe to the cross-origin landing page
    enter_iframe(page, "cross-iframe")
    page.click_on("navigate-to-landing")

    # Ask for the camera there and refuse the request
    enter_iframe(page, "cross-iframe")
    page.click_on("camera-only")
    nav.handle_permission_prompt(button_type="secondary")

    # Come back to the main page and refresh it
    page.switch_to_default_frame()
    nav.click_back_button()
    driver.refresh()

    # The camera is still allowed thanks to the remembered decision: the stream
    # restarts on its own and no permission prompt is raised again
    expect_camera_and_microphone_running(page)
    nav.element_not_visible("popup-notification")
