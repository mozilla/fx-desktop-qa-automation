from pathlib import Path
from shutil import copyfile

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi
from modules.page_base import BasePage
from modules.page_object import AboutPrefs, GenericPage

DEFAULT_ZOOM_110 = 110
DEFAULT_ZOOM_100 = 100
WEBSITE_1 = "https://en.wikipedia.org/wiki/Mozilla"
LOCAL_HTML = "basic_webpage.html"


@pytest.fixture()
def local_doc_path(tmp_path):
    loc = tmp_path / LOCAL_HTML
    copyfile(f"data/pages/{LOCAL_HTML}", loc)
    # copy goomy too!
    copyfile("data/goomy.png", tmp_path / "goomy.png")
    return loc


@pytest.fixture()
def test_case():
    return "545733"


@pytest.fixture()
def temp_selectors():
    return {
        "site-1-image": {
            "selectorData": "a[href='/wiki/File:Mozilla_2024_logo.svg'] > img",
            "strategy": "css",
            "groups": ["doNotCache"],
        },
        "site-1-text": {
            "selectorData": "History",
            "strategy": "id",
            "groups": ["doNotCache"],
        },
        "site-2-image": {
            "selectorData": "goomy",
            "strategy": "class",
            "groups": ["doNotCache"],
        },
        "site-2-text": {
            "selectorData": "para",
            "strategy": "class",
            "groups": ["doNotCache"],
        },
    }


@pytest.fixture()
def add_to_prefs_list():
    """
    Set the pref to zoom text only (simulate after restart)
    """
    return [("browser.zoom.full", False)]


@pytest.fixture()
def web_page(driver: Firefox, temp_selectors):
    """
    return instance of generic page with a given website
    """
    generic_page = GenericPage(driver, url=WEBSITE_1)
    generic_page.elements |= temp_selectors
    generic_page.open()
    yield generic_page


def _capture_element_layout(page: BasePage, selector: str) -> dict:
    el = page.get_element(selector)
    return {"loc": tuple(el.location.values()), "size": tuple(el.size.values())}


def _confirm_element_size(
    page: BasePage,
    selector: str,
    original_value,
    fail_on_change=True,
):
    def _compare(d):
        new_info = _capture_element_layout(page, selector)
        if fail_on_change:
            # Image check: only size matters — images are replaced content,
            # immune to text-only zoom regardless of position shifts.
            changed = new_info.get("size") != original_value.get("size")
        else:
            # Text check: compare full layout. The heading may not reflow
            # but its y-position shifts as text above it expands.
            changed = new_info != original_value
        return changed != fail_on_change

    page.expect(_compare)


@pytest.mark.noxvfb
def test_zoom_text_only_from_settings(
    driver: Firefox, web_page: GenericPage, local_doc_path: Path
):
    """
    C545733.1: Verify that ticking the zoom text only box would only affect the scale of text.
    Verify setting the default zoom level applies the chosen zoom level to all websites.

    Arguments:
        web_page: instance of generic page.
    """
    # Initializing objects
    nav = Navigation(driver)
    panel_ui = PanelUi(driver)

    # Save the original sizes and positions for comparison
    original_layout = {}
    el_types = ["image", "text"]
    for et in el_types:
        index = f"site-1-{et}"
        original_layout[index] = _capture_element_layout(web_page, index)

    # Set the pref to zoom text only
    panel_ui.open_and_switch_to_new_window("tab")
    about_prefs = AboutPrefs(driver, category="General").open()
    about_prefs.click_zoom_text_only()

    # Set zoom level to 110%
    about_prefs.set_default_zoom_level(DEFAULT_ZOOM_110)

    # Confirm that text changes size but image does not
    driver.switch_to.window(driver.window_handles[0])
    _confirm_element_size(
        web_page, "site-1-text", original_layout["site-1-text"], fail_on_change=False
    )
    _confirm_element_size(
        web_page,
        "site-1-image",
        original_layout["site-1-image"],
    )

    panel_ui.open_and_switch_to_new_window("tab")
    nav.search(str(local_doc_path))
    web_page.url_contains(str(local_doc_path))
    for et in el_types:
        index = f"site-2-{et}"
        original_layout[index] = _capture_element_layout(web_page, index)

    driver.switch_to.window(driver.window_handles[1])  # prefs
    about_prefs.set_default_zoom_level(DEFAULT_ZOOM_100)

    # Confirm that the text, not the image, zooms out to 100%, for both sites
    driver.switch_to.window(driver.window_handles[0])  # wiki
    _confirm_element_size(
        web_page,
        "site-1-text",
        original_layout["site-1-text"],
    )
    _confirm_element_size(web_page, "site-1-image", original_layout["site-1-image"])

    driver.switch_to.window(driver.window_handles[2])  # local
    # Local page's "original" was after zoom default changed
    _confirm_element_size(
        web_page, "site-2-text", original_layout["site-2-text"], fail_on_change=False
    )
    _confirm_element_size(web_page, "site-2-image", original_layout["site-2-image"])
