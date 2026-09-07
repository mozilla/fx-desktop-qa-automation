from shutil import copyfile

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support.select import Select

from modules.page_object import AboutPrefs, GenericPage

LOCAL_HTML = "font_settings_page.html"
PAGE_FONT = "Pacifico"


@pytest.fixture()
def about_prefs_category():
    # The Fonts section lives in Settings > Accessibility.
    return "accessibility"


@pytest.fixture()
def test_case():
    return "3370446"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


@pytest.fixture()
def local_doc_path(tmp_path):
    loc = tmp_path / LOCAL_HTML
    copyfile(f"data/pages/{LOCAL_HTML}", loc)
    return f"file://{loc}"


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


def _text_width(test_page: GenericPage, selector: str) -> float:
    """Return the width of a line of text, which follows the font in use."""
    return test_page.get_element(selector).size["width"]


def test_change_font_family(
    driver: Firefox, about_prefs: AboutPrefs, local_doc_path: str, temp_selectors: dict
):
    """
    C3370446 - The font family picked in Settings is used for web page text.
    """
    test_page = GenericPage(driver, url=local_doc_path)
    test_page.elements |= temp_selectors
    test_page.open()

    custom_width = _text_width(test_page, "custom-font-text")
    reference_width = _text_width(test_page, "reference-font-text")
    # The reference text has no font of its own, so it shows the default font.
    default_font = test_page.get_element("reference-font-text").value_of_css_property(
        "font-family"
    )

    about_prefs.open()
    font_select = Select(about_prefs.get_element("font-family-select"))
    # The first option is the default font, so pick another one by name.
    default_label = font_select.options[0].get_attribute("label")
    chosen_font = next(
        value
        for option in font_select.options
        if (value := option.get_attribute("value")) and value not in default_label
    )
    font_select.select_by_value(chosen_font)

    test_page.open()
    # The reference text is drawn in the chosen font now.
    assert _text_width(test_page, "reference-font-text") != reference_width, (
        f"The reference text was not redrawn in {chosen_font}"
    )
    # Pages are still allowed their own fonts, so the page's font is kept.
    assert (
        test_page.get_element("custom-font-text").value_of_css_property("font-family")
        == PAGE_FONT
    )

    about_prefs.open()
    about_prefs.click_on("advanced-fonts-button")
    about_prefs.get_and_switch_iframe()
    about_prefs.click_on("allow-page-fonts-checkbox")
    about_prefs.click_on("fonts-dialog-accept-button")
    about_prefs.switch_to_default_frame()

    test_page.open()
    # Firefox puts its own font first, ahead of the font the page asked for.
    custom_font = test_page.get_element("custom-font-text").value_of_css_property(
        "font-family"
    )
    assert custom_font.startswith(default_font), (
        f"The page font is still first in {custom_font}"
    )
    assert _text_width(test_page, "custom-font-text") != custom_width, (
        f"The page text was not redrawn in {chosen_font}"
    )
