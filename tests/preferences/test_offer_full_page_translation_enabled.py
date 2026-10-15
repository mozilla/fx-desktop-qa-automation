from pathlib import Path

import pytest
from pytest_httpserver import HTTPServer
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TranslationsPanel
from modules.page_object import AboutPrefs

# Without this Nightly has no translation models, so nothing is offered.
REMOTE_SETTINGS_SERVER = "https://firefox.settings.services.mozilla.com/v2"
LOCAL_HTML = "german_article.html"


@pytest.fixture()
def about_prefs_category():
    # The Translations card lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3399160"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.settings-redesign.enabled", True),
        ("browser.translations.enable", True),
        ("services.settings.server", REMOTE_SETTINGS_SERVER),
    ]


@pytest.fixture()
def german_page(httpserver: HTTPServer) -> str:
    """A page in a language other than the browser's.

    Served over http because file:// URLs get no automatic translation offer.
    """
    html = (Path("data/pages") / LOCAL_HTML).read_text(encoding="utf-8")
    httpserver.expect_request(f"/{LOCAL_HTML}").respond_with_data(
        html, content_type="text/html; charset=utf-8"
    )
    return httpserver.url_for(f"/{LOCAL_HTML}")


def test_offer_full_page_translation_enabled(
    driver: Firefox, about_prefs: AboutPrefs, german_page: str
):
    """
    C3399160 - The 'Offer full page translation' option works correctly.
    """
    nav = Navigation(driver)
    translations_panel = TranslationsPanel(driver)
    translations_panel.allow_automatic_popup()

    # The option is on by default.
    about_prefs.open()
    about_prefs.element_attribute_is("offer-translations-checkbox", "checked", "true")

    # Loading a German page offers a translation without being asked.
    nav.search(german_page)
    translations_panel.element_visible("translations-panel")
