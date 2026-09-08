import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs


@pytest.fixture()
def about_prefs_category():
    # The Website language card lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3399158"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


LANGUAGES = ["fr", "es"]


def test_website_language_can_be_reordered(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3399158 - Languages in the 'Website language' can be reordered.
    """
    about_prefs.open()
    about_prefs.element_visible("website-language-heading")

    # Add each language, newest first, then confirm the starting order.
    for language in LANGUAGES:
        about_prefs.add_website_language(language)
        about_prefs.element_visible("website-language-item", labels=[language])
    original_order = about_prefs.get_website_language_order()

    # Move Down on the first language swaps it with the one below it.
    about_prefs.move_website_language(original_order[0], "down")
    moved_down = [original_order[1], original_order[0], *original_order[2:]]
    about_prefs.expect(lambda _: about_prefs.get_website_language_order() == moved_down)

    # Move Up puts it back where it started.
    about_prefs.move_website_language(original_order[0], "up")
    about_prefs.expect(
        lambda _: about_prefs.get_website_language_order() == original_order
    )
