import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi
from modules.page_object_customize_firefox import CustomizeFirefox


@pytest.fixture()
def test_case():
    return "2359315"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.privatebrowsing.resetPBM.enabled", True),
        ("browser.privatebrowsing.felt-privacy-v1", True),
    ]


def test_end_private_session_button_can_be_removed_and_added_back_on_toolbar_via_customize_page(
    driver: Firefox, nav: Navigation, panel_ui: PanelUi
):
    """
    C2359315 - Verify that "End Private Session" button can be removed and added back on the
    toolbar via the Customize page in a Private Window
    """
    # Instantiate objects
    custom_page = CustomizeFirefox(driver)

    # Open a Private window and switch to it
    panel_ui.open_and_switch_to_new_window("private")

    # Open the Customize page
    panel_ui.open_panel_menu()
    panel_ui.navigate_to_customize_toolbar()

    # Remove the End private session button and click Done
    custom_page.remove_widget_from_toolbar("end-private-session")
    custom_page.submit_the_changes_via_done_button()

    # Verify the button is removed from the toolbar
    nav.element_not_visible("end-private-session-button")

    # Go to the Customize page again and Restore Defaults
    panel_ui.open_panel_menu()
    panel_ui.navigate_to_customize_toolbar()
    custom_page.restore_defaults()
    custom_page.submit_the_changes_via_done_button()

    # Verify the end private session button is correctly displayed on the toolbar
    nav.element_visible("end-private-session-button")
