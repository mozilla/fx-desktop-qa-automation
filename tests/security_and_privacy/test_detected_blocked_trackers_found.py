from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TrackerPanel
from modules.page_object import GenericPage


def test_detected_blocked_trackers_found(driver: Firefox):
    """
    C446392: Ensure that the correct trackers are allowed and blocked
    """
    generic_page = GenericPage(driver, url="https://www.bbc.com/")
    tracker_panel = TrackerPanel(driver)
    nav = Navigation(driver).open()

    generic_page.open()
    tracker_panel.wait_for_blocked_tracking_icon(nav, generic_page)
    driver.set_context(driver.CONTEXT_CHROME)
    nav.open_tracker_panel()

    # instantiate test specific objs
    blocked = set(["Cross-Site Tracking Cookies"])
    allowed = set(["Tracking Content"])

    # verify the types of trackers
    if not tracker_panel.verify_allowed_blocked_trackers(allowed, blocked):
        assert False, "The expected types of trackers were not in the correct section."
