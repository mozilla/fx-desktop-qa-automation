import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi, TrustPanel
from modules.page_object import GenericPage

TEST_URL = "https://edition.cnn.com/"


@pytest.fixture()
def test_case():
    return "446434"


def test_tp_settings_private_browsing(
    driver: Firefox, nav: Navigation, panel_ui: PanelUi, trust_panel: TrustPanel
):
    """
    C446434 - TP settings in Private Browsing
    """

    # Instantiate objects
    test_page = GenericPage(driver, url=TEST_URL)

    # Access test website in a new tab
    panel_ui.open_and_switch_to_new_window("tab")
    test_page.open()
    normal_window = driver.current_window_handle

    # Open a new private window and load the same website
    panel_ui.open_and_switch_to_new_window("private")
    private_window = driver.current_window_handle
    test_page.open()

    # The shield icon is displayed (the "✓" one)
    trust_panel.element_visible("shield-icon")
    trust_panel.element_not_visible("shield-icon-disabled")

    # TP is ON in the normal window as well, shield icon has a "✓" in it
    driver.switch_to.window(normal_window)
    trust_panel.element_visible("shield-icon")
    trust_panel.element_not_visible("shield-icon-disabled")

    # Switch off tracking protection in normal window for the site via toggle button
    trust_panel.open_panel()
    trust_panel.trustpanel_toggle_on_off()

    # Tracking protection is switched off in normal window, shield icon has an "x" in it
    trust_panel.element_visible("shield-icon-disabled")
    trust_panel.open_panel()
    trust_panel.trustpanel_status("off")

    # Refresh the https://edition.cnn.com/ website from private window
    driver.switch_to.window(private_window)
    nav.click_on("refresh-button")

    # TP is ON, shield icon has a "✓" in it
    trust_panel.element_visible("shield-icon")
    trust_panel.element_not_visible("shield-icon-disabled")

    # Switch off tracking protection in private window via toggle button
    trust_panel.open_panel()
    trust_panel.trustpanel_toggle_on_off()

    # Shield icon has a "x" inside
    trust_panel.element_visible("shield-icon-disabled")
    trust_panel.open_panel()
    trust_panel.trustpanel_status("off")

    # Refresh the https://edition.cnn.com/ website from normal window
    driver.switch_to.window(normal_window)
    nav.click_on("refresh-button")

    # TP is OFF, shield icon has a "x" inside
    trust_panel.element_visible("shield-icon-disabled")
    trust_panel.open_panel()
    trust_panel.trustpanel_status("off")
