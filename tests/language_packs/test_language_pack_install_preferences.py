import sys
from os import environ

import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs
from modules.util import BrowserActions

LANGUAGES = [("it", "Imposta alternative")]


WIN_GHA = environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("win")


@pytest.mark.skipif(WIN_GHA, reason="Test unstable in Windows Github Actions")
@pytest.mark.parametrize("shortform, localized_text", LANGUAGES)
def test_language_pack_install_about_preferences(
    driver: Firefox, shortform: str, localized_text: str
):
    """
    C1549409: language packs can be installed from about:preferences and firefox is correctly localized
    """
    # instantiate objects
    about_prefs = AboutPrefs(driver, category="general")
    about_prefs.open()
    about_prefs.set_alternative_language(shortform)

    # redo the page object since the browsing context is gone
    about_prefs = AboutPrefs(driver, category="general")
    about_prefs.open()
    about_prefs.element_attribute_contains(
        "language-set-alternative-button", "label", localized_text
    )
