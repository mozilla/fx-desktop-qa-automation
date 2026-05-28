import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "1549409"


LANGUAGES = [("it", "Lingua")]


@pytest.mark.parametrize("shortform, localized_text", LANGUAGES)
def test_language_pack_install_about_preferences(
    driver: Firefox, shortform: str, localized_text: str
):
    """
    C1549409: language packs can be installed from about:preferences and firefox is correctly localized
    """
    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="paneLanguages")

    about_prefs.open()
    about_prefs.set_alternative_language(shortform)

    about_prefs.open()
    about_prefs.element_attribute_contains(
        "browser-language-heading", "label", localized_text
    )
