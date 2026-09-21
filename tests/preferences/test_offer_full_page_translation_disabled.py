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
    return "3399161"


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


def test_offer_full_page_translation_disabled(
    driver: Firefox, about_prefs: AboutPrefs, german_page: str
):
    """
    C3399161 - Disabling 'Offer full page translation' doesn't open the translation panel.
    """
    nav = Navigation(driver)
    translations_panel = TranslationsPanel(driver)
    translations_panel.allow_automatic_popup()

    # Turn the option off.
    about_prefs.open()
    about_prefs.click_on("offer-translations-checkbox-input")
    about_prefs.element_attribute_is_not(
        "offer-translations-checkbox", "checked", "true"
    )

    # A German page only gets the URL bar button, the panel stays closed.
    nav.search(german_page)
    translations_panel.element_visible("translations-urlbar-button")
    translations_panel.element_not_visible("translations-panel")
