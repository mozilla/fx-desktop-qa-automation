from pathlib import Path
from shutil import copyfile

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support.select import Select

from modules.page_object import AboutPrefs, GenericPage

LOCAL_HTML = "font_settings_page.html"
# Any size other than the default works here, and the test checks that below.
NEW_FONT_SIZE = "20"
PAGE_FONT_SIZE = "28px"


@pytest.fixture()
def about_prefs_category():
    # The Fonts section lives in Settings > Accessibility.
    return "accessibility"


@pytest.fixture()
def test_case():
    return "3370695"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


@pytest.fixture()
def local_doc_path(tmp_path: Path) -> str:
    source = Path("data/pages") / LOCAL_HTML
    destination = tmp_path / LOCAL_HTML
    copyfile(source, destination)
    return destination.as_uri()


@pytest.fixture()
def temp_selectors():
    return {
        "custom-font-text": {
            "selectorData": "custom-font",
            "strategy": "class",
            "groups": ["doNotCache"],
        },
        "reference-font-text": {
            "selectorData": "reference-font",
            "strategy": "class",
            "groups": ["doNotCache"],
        },
    }


def _font_sizes(test_page: GenericPage) -> tuple[str, str]:
    """Return the font sizes of the custom and the reference paragraph."""
    return (
        test_page.get_element("custom-font-text").value_of_css_property("font-size"),
        test_page.get_element("reference-font-text").value_of_css_property("font-size"),
    )


def test_change_font_size(
    driver: Firefox, about_prefs: AboutPrefs, local_doc_path: str, temp_selectors: dict
):
    """
    C3370695 - The font size chosen in Settings is used for text that does not set
    its own size.
    """
    test_page = GenericPage(driver, url=local_doc_path)
    test_page.elements |= temp_selectors
    test_page.open()

    # The page sets its own size, the reference text uses the default one.
    custom_size, default_size = _font_sizes(test_page)
    assert custom_size == PAGE_FONT_SIZE
    assert default_size != f"{NEW_FONT_SIZE}px"

    about_prefs.open()
    Select(about_prefs.get_element("font-size-select")).select_by_value(NEW_FONT_SIZE)

    test_page.open()
    assert _font_sizes(test_page) == (PAGE_FONT_SIZE, f"{NEW_FONT_SIZE}px")

    about_prefs.open()
    about_prefs.click_on("advanced-fonts-button")
    about_prefs.get_and_switch_iframe()
    about_prefs.click_on("allow-page-fonts-checkbox")
    about_prefs.click_on("fonts-dialog-accept-button")
    about_prefs.switch_to_default_frame()

    # Blocking the page's own fonts changes the font family, not the sizes.
    test_page.open()
    assert _font_sizes(test_page) == (PAGE_FONT_SIZE, f"{NEW_FONT_SIZE}px")
