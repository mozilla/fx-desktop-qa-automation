import pytest
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By

from modules.browser_object import MenuBar, Navigation, PanelUi, TabBar, TrustPanel
from modules.page_object import AboutCache, AboutDownloads, AboutPrefs, GenericPage
from modules.util import BrowserActions

YOUTUBE_URL = "https://www.youtube.com/"
FACEBOOK_URL = "https://www.facebook.com/"
AMAZON_URL = "https://www.amazon.com/"


@pytest.fixture()
def suite_id():
    return ("5833", "Security and Privacy")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture."""
    prefs = [
        ("browser.urlbar.scotchBonnet.enableOverride", True),
    ]
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []


@pytest.fixture()
def nav(driver):
    return Navigation(driver)


@pytest.fixture()
def about_prefs_privacy(driver):
    return AboutPrefs(driver, category="privacy")


@pytest.fixture()
def trust_panel(driver):
    return TrustPanel(driver)


@pytest.fixture()
def panel_ui(driver):
    return PanelUi(driver)


@pytest.fixture()
def tabs(driver):
    return TabBar(driver)


@pytest.fixture()
def about_cache(driver):
    return AboutCache(driver)


@pytest.fixture()
def about_downloads(driver):
    return AboutDownloads(driver)


@pytest.fixture()
def menu_bar(driver):
    return MenuBar(driver)


@pytest.fixture()
def ba(driver):
    return BrowserActions(driver)


@pytest.fixture()
def websites():
    return [YOUTUBE_URL, FACEBOOK_URL, AMAZON_URL]


@pytest.fixture()
def check_tracker_test_field(driver):
    """Validate tracker results after the test opens the tracker page."""
    its_a_tracker = GenericPage(
        driver,
        url="https://www.itisatrap.org/firefox/its-a-tracker.html",
    )
    field_order = ["third-party", "first-party", "dnt"]

    its_a_tracker.elements |= {
        "test-list-item": {
            "selectorData": "#tests .trackers li",
            "strategy": "css",
            "groups": ["doNotCache"],
        }
    }

    def _check_tracker_test_field(field, correct=True):
        field_index = field_order.index(field)
        result_class = "correct" if correct else "incorrect"

        def _result_is_visible(_):
            try:
                test_items = its_a_tracker.get_elements("test-list-item")

                if len(test_items) <= field_index:
                    return False

                result_element = test_items[field_index].find_element(
                    By.CLASS_NAME,
                    result_class,
                )
                element_classes = result_element.get_attribute("class") or ""

                return "hidden" not in element_classes
            except (
                NoSuchElementException,
                StaleElementReferenceException,
            ):
                return False

        its_a_tracker.expect(_result_is_visible)

    return _check_tracker_test_field
