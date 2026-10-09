import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi, TabBar
from modules.page_object import AboutPrefs


@pytest.fixture()
def about_prefs_category():
    # The Preferred language dropdown lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3399151"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.settings-redesign.enabled", True),
        ("intl.multilingual.enabled", True),
        ("intl.multilingual.downloadEnabled", True),
        ("intl.multilingual.liveReload", True),
    ]


# Locale code, and the Browser language heading once that locale is applied.
LANGUAGES = [("fr", "Langue du navigateur"), ("de", "Browser-Sprache")]


def test_preferred_language_localisation_works(
    driver: Firefox,
    about_prefs: AboutPrefs,
    nav: Navigation,
    panel_ui: PanelUi,
    tabs: TabBar,
):
    """
    C3399151 - Preferred language localisation works as expected.
    """
    preferred, preferred_heading = LANGUAGES[0]
    fallback = LANGUAGES[1][0]

    # Browser toolbar text to check, as (model, element, attribute).
    chrome_strings = [
        (nav, "awesome-bar", "placeholder"),
        (nav, "back-button", "label"),
        (panel_ui, "panel-ui-button", "tooltiptext"),
        (tabs, "newtab-button", "label"),
    ]

    about_prefs.open()
    about_prefs.element_visible("browser-language-heading")

    # Save the English text first.
    english = [
        model.get_attribute_value(element, attr)
        for model, element, attr in chrome_strings
    ]
    assert all(english), "Some toolbar text is empty in English."

    # Picking a language that isn't downloaded yet installs its language pack.
    for language, _ in LANGUAGES:
        about_prefs.set_alternative_language(language)
        about_prefs.expect(
            lambda _, lang=language: (
                lang in about_prefs.get_installed_browser_languages()
            )
        )

    # Reopening the pane still lists every downloaded language.
    about_prefs.open()
    downloaded = about_prefs.get_installed_browser_languages()
    for language, _ in LANGUAGES:
        assert language in downloaded, f"{language} is missing from the dropdown."

    # Switch the Preferred language and check the page is translated.
    about_prefs.set_alternative_language(preferred, wait_for_ui=True)
    about_prefs.element_attribute_contains(
        "browser-language-heading", "label", preferred_heading
    )
    about_prefs.element_visible("browser-language-fallback")

    # The toolbar text is translated too.
    for (model, element, attr), text in zip(chrome_strings, english):
        model.element_attribute_is_not(element, attr, text)
    translated = [
        model.get_attribute_value(element, attr)
        for model, element, attr in chrome_strings
    ]
    assert all(translated), "Some toolbar text is empty after switching language."

    # Changing the fallback does not change the browser language.
    about_prefs.set_fallback_language(fallback)
    about_prefs.element_attribute_is("browser-language-preferred", "value", preferred)
    about_prefs.element_attribute_contains(
        "browser-language-heading", "label", preferred_heading
    )
    for (model, element, attr), text in zip(chrome_strings, translated):
        model.element_attribute_is(element, attr, text)
