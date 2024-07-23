from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi, TrackerPanel
from modules.page_object import GenericPage

ALLOWED_TRACKING_URLS = set(
    [
        "https://content-track-digest256.dummytracker.org",
        "https://ads-track-digest256.dummytracker.org",
        "https://social-track-digest256.dummytracker.org",
        "https://analytics-track-digest256.dummytracker.org",
    ]
)
BLOCKED_TRACKER_URL = "https://content-track-digest256.dummytracker.org"

FIRST_TRACKER_WEBSITE = "https://senglehardt.com/test/trackingprotection/test_pages/tracking_protection.html"
SECOND_TRACKER_WEBSITE = "https://www.itisatrap.org/firefox/its-a-tracker.html"


def test_third_party_content_blocked_private_browsing_cross_site(driver: Firefox, screenshot):
    """
    C446323.1: Ensure that third party content is blocked correctly
    """
    # instantiate objects
    panel_ui = PanelUi(driver).open()
    nav = Navigation(driver)
    tracker_panel = TrackerPanel(driver)
    tracker_website = GenericPage(driver, url=FIRST_TRACKER_WEBSITE)

    # open the new window
    panel_ui.open_private_window()
    nav.switch_to_new_window()

    # open the website, ensure the blocking is taking place by continuously refreshing website until indicated
    tracker_website.open()
    tracker_panel.wait_for_blocked_tracking_icon(nav, tracker_website, screenshot)

    # verify the indicator
    driver.set_context(driver.CONTEXT_CHROME)
    tracker_panel.verify_tracker_shield_indicator(nav)
    nav.open_tracker_panel()

    # verify the panel title
    tracker_panel_title = tracker_panel.get_element("tracker-title")
    assert (
        tracker_panel_title.get_attribute("innerHTML")
        == "Protections for senglehardt.com"
    )

    # fetch the items in the cross site trackers
    cross_site_trackers = tracker_panel.open_and_return_cross_site_trackers()

    # ensure that the correct blocked site is listed
    found_tracker = False
    for item in cross_site_trackers:
        if item.get_attribute("value") == BLOCKED_TRACKER_URL:
            found_tracker = True
    assert found_tracker


def test_third_party_content_blocked_private_browsing_allowed_tracking(driver: Firefox, screenshot):
    """
    C446323.2: Ensure that some third party content is allowed
    """
    # instantiate objects
    panel_ui = PanelUi(driver).open()
    nav = Navigation(driver)
    tracker_panel = TrackerPanel(driver)
    tracker_website = GenericPage(driver, url=FIRST_TRACKER_WEBSITE)

    # open a private window
    panel_ui.open_private_window()
    nav.switch_to_new_window()

    # open the website, ensure the blocking is taking place by continuously refreshing website until indicated
    tracker_website.open()
    tracker_panel.wait_for_blocked_tracking_icon(nav, tracker_website, screenshot)

    # verify the indicator
    driver.set_context(driver.CONTEXT_CHROME)
    tracker_panel.verify_tracker_shield_indicator(nav)

    # open the panel and verify the title
    nav.open_tracker_panel()
    tracker_panel_title = tracker_panel.get_element("tracker-title")
    assert (
        tracker_panel_title.get_attribute("innerHTML")
        == "Protections for senglehardt.com"
    )

    # fetch allowed trackers
    allowed_trackers = tracker_panel.open_and_return_allowed_trackers()

    # verify the correct ones are allowed
    for item in allowed_trackers:
        assert item.get_attribute("value") in ALLOWED_TRACKING_URLS


def test_third_party_content_private_browsing_tracking_statuses(driver: Firefox, screenshot):
    """
    C446323.3: Ensure that the statuses of some third party content are loaded properly
    """
    # instantiate objects
    panel_ui = PanelUi(driver).open()
    nav = Navigation(driver)
    tracker_panel = TrackerPanel(driver)
    tracker_website = GenericPage(driver, url=SECOND_TRACKER_WEBSITE)

    # open a private window
    panel_ui.open_private_window()
    nav.switch_to_new_window()

    # open the tracker website
    tracker_website.open()
    tracker_panel.wait_for_blocked_tracking_icon(nav, tracker_website, screenshot)

    # verify the indicator
    tracker_panel.verify_tracker_shield_indicator(nav)

    # assert all of the various statuses, ensure that the correct one is displayed
    block_status = tracker_website.get_element("simulated-tracker-block-status")
    load_status = tracker_website.get_element("simulated-tracker-load-status")
    dnt_status = tracker_website.get_element("simulated-tracker-dnt-status")

    assert "hidden" not in block_status.get_attribute("class")
    assert "hidden" not in load_status.get_attribute("class")
    assert "hidden" not in dnt_status.get_attribute("class")
