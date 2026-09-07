from itertools import islice
from shutil import copyfile

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support.select import Select

from modules.page_object import AboutPrefs, GenericPage

LOCAL_HTML = "font_settings_page.html"
PAGE_FONT = "Pacifico"
GENERIC_FONTS = ("serif", "sans-serif", "monospace", "cursive", "fantasy")
FONTS_TO_TRY = 3


@pytest.fixture()
def about_prefs_category():
    # The Fonts section lives in the Accessibility settings.
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
    # The reference text has no font, so it shows the generic default, serif.
    default_font = test_page.get_element("reference-font-text").value_of_css_property(
        "font-family"
    )

    about_prefs.open()
    font_select = Select(about_prefs.get_element("font-family-select"))
    # Skip the generic names Linux lists, they would not change the page.
    candidates = list(
        islice(
            (
                value
                for option in font_select.options
                if (value := option.get_attribute("value"))
                and value not in GENERIC_FONTS
            ),
            FONTS_TO_TRY,
        )
    )
    assert candidates, "The font family dropdown lists only generic fonts"

    # Two fonts can share letter widths, so try a few. Settings is open now.
    chosen_font = None
    for candidate in candidates:
        Select(about_prefs.get_element("font-family-select")).select_by_value(candidate)
        test_page.open()
        # The reference text is drawn in the chosen font now.
        if _text_width(test_page, "reference-font-text") != reference_width:
            chosen_font = candidate
            break
        about_prefs.open()

    assert chosen_font, f"None of {candidates} redrew the reference text"
    # Pages can still choose their own fonts, so the page font is kept.
    page_font = test_page.get_element("custom-font-text").value_of_css_property(
        "font-family"
    )
    assert page_font.startswith(PAGE_FONT), f"The page font is not first in {page_font}"

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
