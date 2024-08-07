from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import TabBar
from modules.page_object import ExamplePage


def test_open_new_via_hyperlink(driver: Firefox):
    """
    C134444 - A hyperlink can be opened in a new tab
    """
    browser = TabBar(driver)
    example = ExamplePage(driver).open()

    # Use context menu option to open link in new tab
    example.context_click("more-information")
    browser.set_chrome_context()
    menu_option = driver.find_element(By.ID, "context-openlinkintab")
    menu_option.click()
    browser.hide_popup("contentAreaContextMenu")

    # Get the title of the new tab
    browser.click_tab_by_index(2)
    browser.expect(EC.title_contains("Example Domains"))
