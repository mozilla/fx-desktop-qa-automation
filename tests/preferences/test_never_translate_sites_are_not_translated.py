from pathlib import Path
from urllib.parse import urlparse

import pytest
from pytest_httpserver import HTTPServer
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TranslationsPanel
from modules.page_object import AboutPrefs, GenericPage

# Without this Nightly has no translation models, so nothing is offered.
REMOTE_SETTINGS_SERVER = "https://firefox.settings.services.mozilla.com/v2"

LOCAL_HTML = "german_article.html"
GERMAN_HEADING = "Der Wald im Herbst"


@pytest.fixture()
def about_prefs_category():
    # The Translations card lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3399534"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.settings-redesign.enabled", True),
        ("browser.translations.enable", True),
        ("services.settings.server", REMOTE_SETTINGS_SERVER),
        # Off for now, or the first visit uses up the site's one popup.
        ("browser.translations.automaticallyPopup", False),
    ]


@pytest.fixture()
def german_page(httpserver: HTTPServer) -> str:
    """A page in a language other than the browser's.

    Served over http because the never-translate list is keyed by origin.
    """
    html = (Path("data/pages") / LOCAL_HTML).read_text(encoding="utf-8")
    httpserver.expect_request(f"/{LOCAL_HTML}").respond_with_data(
        html, content_type="text/html; charset=utf-8"
    )
    return httpserver.url_for(f"/{LOCAL_HTML}")


def test_never_translate_sites_are_not_translated(
    driver: Firefox, about_prefs: AboutPrefs, german_page: str
):
    """
    C3399534 - Websites added in the 'Never translate these sites' section are NOT translated.
    """
    nav = Navigation(driver)
    translations_panel = TranslationsPanel(driver)
    parts = urlparse(german_page)
    origin = f"{parts.scheme}://{parts.netloc}"

    # Open the Translations sub-pane, then block the German page from the gear menu.
    about_prefs.open()
    about_prefs.open_more_translation_settings()
    nav.search(german_page)
    translations_panel.open_panel()
    translations_panel.check_never_translate_site()

    # Let the panel pop up on its own again, so we can check that it doesn't.
    about_prefs.open()
    about_prefs.click_on("offer-translations-checkbox-input")
    about_prefs.element_attribute_is("offer-translations-checkbox", "checked", "true")
    translations_panel.allow_automatic_popup()

    # The site is listed back on the Translations sub-pane.
    about_prefs.open_more_translation_settings()
    about_prefs.element_visible("never-translate-site-item", labels=[origin])

    # The icon shows, but the panel stays closed and the text stays German.
    nav.search(german_page)
    translations_panel.element_visible("translations-urlbar-button")
    # The panel was opened before, so check its state, not visibility.
    translations_panel.element_attribute_is("translations-panel", "state", "closed")
    german_article = GenericPage(driver, url=german_page)
    german_article.expect_in_content(
        lambda _: GERMAN_HEADING in german_article.get_element("page-body").text
    )
