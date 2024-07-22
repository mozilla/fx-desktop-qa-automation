import logging
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi, TabBar, TrackerPanel
from modules.page_object import GenericPage

# @pytest.fixture()
# def add_prefs():
#     return [("browser.contentblocking.category", "standard")]


def test_third_party_content_blocked_private_browsing(driver: Firefox):
    """
    C446323: Ensure that third party content is blocked correctly
    """
    panel_ui = PanelUi(driver).open()
    nav = Navigation(driver)
    tracker_panel = TrackerPanel(driver)
    first_tracker_website = GenericPage(
        driver,
        url="https://senglehardt.com/test/trackingprotection/test_pages/tracking_protection.html",
    )
    second_tracker_website = GenericPage(
        driver, url="https://itisatrap.org/firefox/its-a-tracker.html"
    )

    panel_ui.open_private_window()
    nav.switch_to_new_window()

    first_tracker_website.open()

    tracker_panel.wait_for_blocked_tracking_icon(nav, first_tracker_website)

    # first_tracker_website.open()
    driver.set_context(driver.CONTEXT_CHROME)

    shield_icon = nav.get_element("shield-icon")

    # # this could be labelled differently in different versions
    assert (
        shield_icon.get_attribute("data-l10n-id")
        == "tracking-protection-icon-active-container"
    ), "The label detected did not correspond to the expected one: tracking-protection-icon-no-trackers-detected-container"
    nav.open_tracker_panel()

    tracker_panel_title = nav.get_element("tracker-title")
    logging.info(tracker_panel_title.get_attribute("innerHTML"))

    nav.get_element("tracker-cross-site-tracking").click()
