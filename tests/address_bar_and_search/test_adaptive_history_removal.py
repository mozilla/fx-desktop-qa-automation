import pytest
from pytest_httpserver import HTTPServer
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi, TabBar

TYPED_TEXT = "loc"
EXPECTED_IN_TITLE = "Science"


@pytest.fixture()
def test_url(httpserver: HTTPServer) -> str:
    httpserver.expect_request("/science/").respond_with_data(
        f"<html><head><title>{EXPECTED_IN_TITLE}</title></head><body>Science</body></html>",
        content_type="text/html",
    )
    return httpserver.url_for("/science/").replace("127.0.0.1", "localhost")


@pytest.fixture()
def test_case():
    return "3029071"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.urlbar.autoFill.adaptiveHistory.enabled", True)]


def test_adaptive_history_removal(driver: Firefox, test_url: str) -> None:
    """
    C3029071 - Verify adaptive history entry is deleted from history and
    not suggested in address bar.
    """
    # Instantiate objects
    nav = Navigation(driver)
    tabs = TabBar(driver)
    panel = PanelUi(driver)
    expected_url = test_url.removeprefix("http://").rstrip("/")

    # Visit the test site and verify title
    nav.search(test_url)
    tabs.expect_title_contains(EXPECTED_IN_TITLE)

    # Open new tab, close the original
    tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[1])
    tabs.close_first_tab_by_icon()

    # Type in address bar, then click adaptive suggestion
    nav.type_in_awesome_bar(TYPED_TEXT)
    nav.click_firefox_suggest()
    nav.url_contains(test_url)

    # Open new tab and check for autofill suggestion
    tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[-1])
    nav.type_in_awesome_bar(TYPED_TEXT)
    # Adaptive autofill is done through Fx Suggest, url in title attr
    nav.element_attribute_contains(
        "search-result-autofill-adaptive-element",
        "title",
        expected_url,
    )

    # Delete the adaptive history entry
    panel.open_history_menu()
    nav.delete_panel_menu_item_by_title(EXPECTED_IN_TITLE)
    panel.confirm_history_clear()

    # Open new tab and verify the adaptive suggestion is removed
    tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[-1])
    tabs.close_first_tab_by_icon()
    nav.type_in_awesome_bar(TYPED_TEXT)
    nav.wait_for_suggestions_present()
    nav.wait_for_suggestions_complete(TYPED_TEXT)
    # Firefox removes the suggestion when its history entry is deleted.
    nav.element_not_visible(
        "suggestion-url-by-title",
        labels=[expected_url],
    )
