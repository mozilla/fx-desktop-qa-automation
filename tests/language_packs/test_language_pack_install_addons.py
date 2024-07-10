from selenium.webdriver import Firefox

# from modules.page_object import AboutAddons, AboutPrefs
from modules.page_object import AboutAddons, GenericPage

# from modules.util import Utilities

LANGUAGE_ADDONS_LINK = "https://addons.mozilla.org/en-US/firefox/language-tools/"


def test_language_pack_install_from_addons(driver: Firefox):
    """
    C1549408: verify that installing a language pack from about:addons will correctly change the locale
    """
    # about_prefs = AboutPrefs(driver, category="general")
    generic_page = GenericPage(driver)
    # util = Utilities()

    driver.get(LANGUAGE_ADDONS_LINK)

    generic_page.custom_wait(timeout=20).until(
        lambda _: generic_page.get_element("language-addons-title") is not None
    )

    language_row = generic_page.get_element("language-addons-row")
    generic_page.get_element(
        "language-addons-row-link", parent_element=language_row
    ).click()
    generic_page.custom_wait(timeout=20).until(
        lambda _: generic_page.get_element("language-addons-subpage-header") is not None
    )

    generic_page.get_element("language-addons-subpage-add-to-firefox").click()

    with driver.context(driver.CONTEXT_CHROME):
        # click one for "Add"
        generic_page.get_element("language-install-popup-add").click()
        # click second time for "Okay", the button is not cached which allows for two different buttons to be different
        generic_page.get_element("language-install-popup-add").click()

    about_addons = AboutAddons(driver).open()
    about_addons.choose_sidebar_option("locale")

    addon_list_parent = about_addons.get_element("languages-addon-list")
    addon_language_cards = about_addons.get_element(
        "languages-addon-list-card", multiple=True, parent_element=addon_list_parent
    )

    # making sure that 1 language was installed
    assert len(addon_language_cards) == 1
