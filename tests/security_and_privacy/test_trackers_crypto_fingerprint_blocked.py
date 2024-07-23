import logging
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TrackerPanel
from modules.page_object import GenericPage

TRACKER_URL = "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting_and_cryptomining_and_cookies.html"


def test_cross_site_trackrs_crypto_fingerprinter_blocked(driver: Firefox):
    """
    C446393: Ensures that some trackers are blocked on certain website
    """
    tracker_page = GenericPage(driver, url=TRACKER_URL)
    tracker_panel = TrackerPanel(driver)
    nav = Navigation(driver).open()

    tracker_page.open()
    tracker_page.open()
    tracker_panel.wait_for_blocked_tracking_icon(nav, tracker_page)
    nav.open_tracker_panel()

    driver.set_context(driver.CONTEXT_CHROME)
    tracker_item_container = tracker_panel.get_element("tracking-item-container")
    all_tracking_items = tracker_panel.get_all_children(tracker_item_container)

    blocked = set()
    add_blocked = False
    allowed = set()
    add_allowed = False

    for item in all_tracking_items:
        # encounter a blocked header (everything after it is blocked in the list)
        if item.get_attribute("id") == "protections-popup-blocking-section-header":
            add_allowed = False
            add_blocked = True
        elif (
            item.get_attribute("id") == "protections-popup-not-blocking-section-header"
        ):
            add_allowed = True
            add_blocked = False
        else:
            child_labels = tracker_panel.get_element(
                "tracking-item-container-label", multiple=True, parent_element=item
            )
            for child in child_labels:
                label = child.get_attribute("innerHTML")
                if add_blocked:
                    blocked.add(label)
                elif add_allowed:
                    allowed.add(label)

    logging.info(blocked)
    logging.info(allowed)
