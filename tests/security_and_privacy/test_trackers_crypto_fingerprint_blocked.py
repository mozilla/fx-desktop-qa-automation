from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TrackerPanel
from modules.page_object import GenericPage

TRACKER_URL = "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting_and_cryptomining_and_cookies.html"


def test_cross_site_trackrs_crypto_fingerprinter_blocked(driver: Firefox):
    """
    C446393: Ensures that some trackers are blocked on certain website
    """
    # instantiate objs
    tracker_page = GenericPage(driver, url=TRACKER_URL)
    tracker_panel = TrackerPanel(driver)
    nav = Navigation(driver).open()

    # wait for the shield icon
    tracker_page.open()
    tracker_panel.wait_for_blocked_tracking_icon(nav, tracker_page)
    nav.open_tracker_panel()

    # get children
    driver.set_context(driver.CONTEXT_CHROME)
    tracker_item_container = tracker_panel.get_element("tracking-item-container")
    all_tracking_items = tracker_panel.get_all_children(tracker_item_container)

    # instantiate test specific objs
    blocked = set(["Cross-Site Tracking Cookies", "Fingerprinters", "Cryptominers"])
    allowed = set(["Tracking Content"])
    rm_blocked = False
    rm_allowed = False

    for item in all_tracking_items:
        # encounter a header (everything after it is blocked/allowed in the list)
        inner_html = item.get_attribute("innerHTML")
        if "Blocked" in inner_html:
            rm_blocked = True
            continue
        elif "Allowed" in inner_html:
            rm_allowed = True
            rm_blocked = False
            continue

        # assign a temp memory location, assign the set to it depending on the header seen earlier
        rm_set = set()
        to_rm_item = ""
        if rm_blocked:
            rm_set = blocked
        elif rm_allowed:
            rm_set = allowed

        # go through the possible strings to look for, remove it if appropriate
        for item in rm_set:
            if item in inner_html:
                to_rm_item = item
                break
        if to_rm_item != "":
            rm_set.remove(to_rm_item)

    # ensure that we have seen all of the expected items in each section
    assert (
        len(blocked) == 0 and len(allowed) == 0
    ), "Not all of the expected items were found in each of the Blocked/Allowed sections."
