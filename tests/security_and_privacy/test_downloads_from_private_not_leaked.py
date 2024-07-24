from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import HyperlinkContextMenu, PanelUi
from modules.page_object import AboutDownloads, GenericPage


def test_downloads_from_private_not_leaked(driver: Firefox):
    """C101674 - Downloads initiated from a private window are not leaked to the non-private window"""

    # We're going to assume no downloads as every test is run in a new instance
    panelui = PanelUi(driver).open_panel_menu()
    panelui.select_panel_setting("new-private-window-option")
    panelui.wait_for_num_windows(2)
    panelui.switch_to_new_window()

    about_downloads = AboutDownloads(driver)
    about_downloads.open()
    assert about_downloads.is_empty()

    irs_forms = GenericPage(driver, url="https://www.irs.gov/forms-instructions")
    context_menu = HyperlinkContextMenu(driver)
    irs_forms.open()

    pdf_links = irs_forms.get_elements("pdf-links")
    for link in pdf_links[:5]:
        irs_forms.context_click(link)
        context_menu.click_and_hide_menu("context-menu-save-link")
