import pytest

from modules.browser_object import Navigation, PanelUi, TabBar, TrustPanel
from modules.page_object import AboutCache, AboutDownloads, AboutPrefs
from modules.util import BrowserActions

YOUTUBE_URL = "https://www.youtube.com/"
FACEBOOK_URL = "https://www.facebook.com/"
AMAZON_URL = "https://www.amazon.com/"


@pytest.fixture()
def suite_id():
    return ("5833", "Security and Privacy")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = [("browser.urlbar.scotchBonnet.enableOverride", True)]
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
def ba(driver):
    return BrowserActions(driver)


@pytest.fixture()
def websites():
    return [YOUTUBE_URL, FACEBOOK_URL, AMAZON_URL]
