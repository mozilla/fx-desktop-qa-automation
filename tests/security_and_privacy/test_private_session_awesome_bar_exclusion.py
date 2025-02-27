import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_panel_ui import PanelUi


@pytest.fixture()
def test_case():
    return "101665"


YOUTUBE_URL = "https://www.youtube.com/"
FACEBOOK_URL = "https://www.facebook.com/"
AMAZON_URL = "https://www.amazon.com/"

WEBSITES = [YOUTUBE_URL, FACEBOOK_URL, AMAZON_URL]


def test_websites_visited_in_private_browser_not_displayed_in_awesome_bar(
    driver: Firefox,
):
    """
    C101665 - Verify the visited websites from the Private Browsing session are not displayed inside the normal session
    Awesome Bar
    """

    initial_window_handle = driver.current_window_handle
    nav = Navigation(driver)
    panel_ui = PanelUi(driver)

    panel_ui.open_and_switch_to_new_window("private")

    for url in WEBSITES:
        driver.get(url)

    driver.switch_to.window(initial_window_handle)

    for url in WEBSITES:
        nav.type_in_awesome_bar(url)
        with driver.context(driver.CONTEXT_CHROME):
            url_element = nav.get_element("search-result-url")
            action_element = nav.get_element("search-result-action-term")

            # Check that the URLS are displayed in search results with the term "Visit"
            assert (url_element.text, action_element.text) == (url, "Visit")

        nav.clear_awesome_bar()
