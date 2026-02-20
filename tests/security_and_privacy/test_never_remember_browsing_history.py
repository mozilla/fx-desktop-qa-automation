import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi, TabBar
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "102381"


links = [
    "about:about",
    "about:addons",
    "about:cache",
    "about:config",
    "about:buildconfig",
    "about:robots",
    "about:blank",
]

COOKIE_LABEL_TEXT = "Based on your history settings, Firefox deletes cookies and site data from your session when you close the browser."
HISTORY_LABEL_TEXT = "Firefox will use the same settings as private browsing, and will not remember any history as you browse the Web."


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.privatebrowsing.autostart", True)]


def test_never_remember_browsing_history_settings(
    driver: Firefox, about_prefs_privacy: AboutPrefs
):
    """
    C102381.1: Ensure that setting the browser to never remember history has the correct configurations in about:preferences
    """

    # instantiate objs
    about_prefs_privacy.open()

    # perform all about:preferences#privacy assertions according to testrail
    cookies_label = about_prefs_privacy.get_element("cookies-privacy-label")
    assert cookies_label.get_attribute("message") == COOKIE_LABEL_TEXT

    delete_cookies_checkbox = about_prefs_privacy.get_element("cookies-delete-on-close")
    assert delete_cookies_checkbox.get_attribute("checked") == "true"

    save_password = about_prefs_privacy.get_element("logins-ask-to-save-password")
    assert save_password.get_attribute("checked") is None

    login_exceptions = about_prefs_privacy.get_element("logins-exceptions")
    assert login_exceptions.get_attribute("disabled") == "true"

    history_mode_description = about_prefs_privacy.get_element("history-privacy-label")
    assert history_mode_description.get_attribute("description") == HISTORY_LABEL_TEXT


def test_never_remember_browsing_history_from_panel(
    driver: Firefox, panel_ui: PanelUi, tabs: TabBar
):
    """
    C102381.2: Ensure that setting the browser to never remember history does not actually save any history
    """
    panel_ui.open()

    num_tabs = 6

    # open some tabs
    for i in range(num_tabs):
        driver.get(links[i])
        tabs.new_tab_by_button()
        tabs.switch_to_new_tab()

    # close the first 6 tabs
    for i in range(num_tabs):
        tabs.close_tab(tabs.get_tab(num_tabs - i))

    panel_ui.confirm_history_clear()
