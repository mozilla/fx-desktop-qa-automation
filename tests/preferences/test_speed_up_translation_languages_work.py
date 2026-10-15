from pathlib import Path

import pytest
from pytest_httpserver import HTTPServer
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TranslationsPanel
from modules.page_object import AboutPrefs, AboutTranslations, GenericPage

# Without this Nightly has no translation models, so the pickers stay disabled.
REMOTE_SETTINGS_SERVER = "https://firefox.settings.services.mozilla.com/v2"
LOCAL_HTML = "german_article.html"
GERMAN_HEADING = "Der Wald im Herbst"
GERMAN_TEXT = "Die Blätter der Bäume werden gelb, orange und rot."
DOWNLOAD_LANGUAGE = "de"
TARGET_LANGUAGE = "en"
# The model is already downloaded, so this should only take seconds.
FAST_TRANSLATION_TIMEOUT = 20


@pytest.fixture()
def about_prefs_category():
    # The Translations card lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3399176"


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
    """A page in the downloaded language.

    Served over http because file:// URLs get no translation offer.
    """
    html = (Path("data/pages") / LOCAL_HTML).read_text(encoding="utf-8")
    httpserver.expect_request(f"/{LOCAL_HTML}").respond_with_data(
        html, content_type="text/html; charset=utf-8"
    )
    return httpserver.url_for(f"/{LOCAL_HTML}")


def test_speed_up_translation_languages_work(
    driver: Firefox, about_prefs: AboutPrefs, german_page: str
):
    """
    C3399176 - Speed up translation languages work as expected.
    """
    nav = Navigation(driver)
    translations_panel = TranslationsPanel(driver)

    # Download German from the 'Speed up translation' section.
    about_prefs.open()
    about_prefs.open_more_translation_settings()
    about_prefs.download_translation_language(DOWNLOAD_LANGUAGE)
    about_prefs.wait_for_language_download(DOWNLOAD_LANGUAGE)

    # A German page translates within seconds.
    nav.search(german_page)
    translations_panel.open_panel()
    translations_panel.translate_page(timeout=FAST_TRANSLATION_TIMEOUT)
    german_article = GenericPage(driver, url=german_page)
    german_article.expect_in_content(
        lambda _: GERMAN_HEADING not in german_article.get_element("page-body").text
    )

    # about:translations is fast too.
    about_translations = AboutTranslations(driver).open()
    about_translations.select_language("source-select", DOWNLOAD_LANGUAGE)
    about_translations.select_language("target-select", TARGET_LANGUAGE)
    about_translations.translate_text(GERMAN_TEXT, FAST_TRANSLATION_TIMEOUT)
    assert (
        about_translations.get_element("target-textarea").get_attribute("value")
        != GERMAN_TEXT
    )
