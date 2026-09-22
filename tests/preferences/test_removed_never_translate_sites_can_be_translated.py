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
    return "3399170"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.settings-redesign.enabled", True),
        ("browser.translations.enable", True),
        ("services.settings.server", REMOTE_SETTINGS_SERVER),
        # Keep the panel from opening on its own so the test drives it.
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


def test_removed_never_translate_sites_can_be_translated(
    driver: Firefox, about_prefs: AboutPrefs, german_page: str
):
    """
    C3399170 - Websites removed from the 'Never translate these sites' section can be translated.
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

    # The site is listed back on the Translations sub-pane.
    about_prefs.open()
    about_prefs.open_more_translation_settings()
    about_prefs.element_visible("never-translate-site-item", labels=[origin])

    # Deleting it takes the row away.
    about_prefs.remove_never_translate_site(origin)
    about_prefs.element_does_not_exist("never-translate-site-item", labels=[origin])

    # The site is offered again, and translating it swaps the German text out.
    nav.search(german_page)
    translations_panel.element_visible("translations-urlbar-button")
    translations_panel.open_panel()
    translations_panel.translate_page()
    german_article = GenericPage(driver, url=german_page)
    german_article.expect_in_content(
        lambda _: GERMAN_HEADING not in german_article.get_element("page-body").text
    )
