import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import PanelUi
from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "1362731"


HTTP_SITE = "http://example.com"


def test_https_first_mode_in_private_browsing(
    driver: Firefox, about_prefs_privacy: AboutPrefs, panel_ui: PanelUi
):
    """
    C1362731 Check that https First Mode is properly enabled and working in Private Browsing
    """

    # Navigate to the HTTP Site in a Private Window
    about_prefs_privacy.open()
    about_prefs_privacy.select_https_only_setting(
        about_prefs_privacy.HTTPS_ONLY_STATUS.HTTPS_ONLY_PRIVATE
    )
    panel_ui.open_and_switch_to_new_window("private")
    driver.get("about:blank")
    driver.get(HTTP_SITE)

    # Wait for the URL to be redirected to HTTPS

    about_prefs_privacy.url_contains("https://")
