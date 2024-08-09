import json

from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation
from modules.page_object import AboutPrefs, GenericPage

DOC_LINK = "https://sapphire-hendrika-5.tiiny.site/"


def test_mime_type_doc(driver: Firefox):
    """
    C1756748: Verify the user can add the .doc type
    """
    doc_page = GenericPage(driver, url=DOC_LINK).open()
    nav = Navigation(driver)
    context_menu = ContextMenu(driver)
    about_prefs = AboutPrefs(driver, category="general")
    doc_page.get_element("sample-doc-download").click()

    downloads_button = nav.get_download_button()

    with driver.context(driver.CONTEXT_CHROME):
        downloads_button.click()
        download_item = nav.get_element("download-panel-item")
        nav.context_click(download_item)
        context_menu.get_element("context-menu-always-open-similar-files").click()

    about_prefs.open()
    about_prefs.element_exists("mime-type-item", labels=["application/msword"])

    mime_type_item = about_prefs.get_element(
        "mime-type-item", labels=["application/msword"]
    )
    action_description_item = about_prefs.get_element(
        "mime-type-item-description", parent_element=mime_type_item
    )

    mime_type_data = json.loads(action_description_item.get_attribute("data-l10n-args"))
    assert False, mime_type_data["app-name"]
