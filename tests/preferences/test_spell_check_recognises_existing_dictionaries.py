from shutil import copyfile

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu
from modules.page_object import AboutAddons, AboutPrefs, AmoLanguages, GenericPdf

AMO_LANGUAGE_TOOLS_URL = "addons.mozilla.org/en-US/firefox/language-tools"
PDF_FILE_NAME = "i-9.pdf"
TEXT_FIELD = "first-name-field"
MISSPELLED_WORD = "frumoas"

# Language code on AMO and the dictionary add-on id.
DICTIONARIES = [
    ("ro", "ro-RO@www.archeus.ro"),
    ("it", "it-IT@dictionaries.addons.mozilla.org"),
]


@pytest.fixture()
def about_prefs_category():
    # The Spell check card lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3987578"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


@pytest.fixture()
def hard_quit():
    return True


def right_click_word(pdf_viewer: GenericPdf):
    # Right-click near the left edge so we land on the word.
    field = pdf_viewer.get_element(TEXT_FIELD)
    x_offset = -field.size["width"] // 2 + 10
    pdf_viewer.actions.move_to_element_with_offset(
        field, x_offset, 0
    ).context_click().perform()


def test_spell_check_recognises_existing_dictionaries(
    driver: Firefox, about_prefs: AboutPrefs, tmp_path
):
    """
    C3987578 - Spell check recognises existing dictionaries.
    """
    amo_languages = AmoLanguages(driver)
    about_addons = AboutAddons(driver)
    context_menu = ContextMenu(driver)

    # Download dictionaries opens AMO language tools in a new tab.
    about_prefs.open()
    about_prefs.click_on("download-dictionaries-link")
    about_prefs.wait_for_num_tabs(2)
    about_prefs.switch_to_new_tab()
    about_prefs.url_contains(AMO_LANGUAGE_TOOLS_URL)

    # Install each dictionary from the list.
    for code, _ in DICTIONARIES:
        amo_languages.open()
        amo_languages.wait_for_language_page_to_load()
        amo_languages.click_on("language-addons-dictionary-link", labels=[code])
        amo_languages.element_visible("language-addons-subpage-header")
        amo_languages.click_on("language-addons-subpage-add-to-firefox")
        amo_languages.confirm_addon_install_popup()

    # Every dictionary shows up in about:addons.
    about_addons.open()
    about_addons.choose_sidebar_option("dictionary")
    for _, addon_id in DICTIONARIES:
        about_addons.element_visible("addon-card", labels=[addon_id])

    # Open a local PDF form instead of the remote one.
    pdf_path = tmp_path / PDF_FILE_NAME
    copyfile(f"data/{PDF_FILE_NAME}", pdf_path)
    pdf_viewer = GenericPdf(driver, pdf_url=f"file://{pdf_path}")

    # Turn on Check Spelling for the text field.
    pdf_viewer.click_on(TEXT_FIELD)
    pdf_viewer.context_click(TEXT_FIELD)
    context_menu.click_and_hide_menu("context-menu-check-spelling")

    # Every downloaded dictionary is listed under Languages.
    pdf_viewer.context_click(TEXT_FIELD)
    context_menu.click_context_item("context-menu-spell-languages")
    for code, _ in DICTIONARIES:
        context_menu.element_exists("context-menu-spell-dictionary", labels=[code])

    # Turn on the Romanian dictionary.
    context_menu.click_context_item("context-menu-spell-dictionary", labels=["ro"])
    context_menu.hide_popup("contentAreaContextMenu")

    # Reopen the menu to see Romanian is checked.
    pdf_viewer.context_click(TEXT_FIELD)
    context_menu.click_context_item("context-menu-spell-languages")
    context_menu.element_attribute_is(
        "context-menu-spell-dictionary", "checked", "true", labels=["ro"]
    )
    context_menu.hide_popup("contentAreaContextMenu")

    # Keyboard layout can't be changed here, so type the word directly.
    # The trailing space makes spell check look at the word.
    pdf_viewer.fill(TEXT_FIELD, f"{MISSPELLED_WORD} ", press_enter=False)

    # A misspelled word gets spelling suggestions.
    right_click_word(pdf_viewer)
    context_menu.element_visible("context-menu-spell-suggestion")

    # Picking a suggestion fixes the word.
    context_menu.click_and_hide_menu("context-menu-spell-suggestion")
    pdf_viewer.expect(
        lambda _: (
            pdf_viewer.get_element(TEXT_FIELD).get_attribute("value")
            != f"{MISSPELLED_WORD} "
        )
    )

    # The fixed word has no suggestions, so it is no longer underlined.
    right_click_word(pdf_viewer)
    context_menu.element_visible("context-menu-copy")
    context_menu.element_does_not_exist("context-menu-spell-suggestion")
    context_menu.hide_popup("contentAreaContextMenu")
