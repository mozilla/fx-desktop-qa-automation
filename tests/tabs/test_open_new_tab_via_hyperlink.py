import time

from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from modules.browser_object import TabBar


def test_open_new_via_hyperlink(driver: Firefox):
    """
    C134444 - A hyperlink can be opened in a new tab
    """
    browser = TabBar(driver).open()
    driver.get("https://example.com")
    example_link = driver.find_element(By.LINK_TEXT, "More information...")
    browser.actions.context_click(example_link).perform()
    browser.set_chrome_context()
    # BLOCKER: How do I find the context menu option element?
    # This is sending keys to the hyperlink
    # browser.actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
    in_tab = driver.find_element(By.ID, "context-openlinkintab")
    in_tab.click()
    # Get the title of the new tab
    browser.click_tab_by_index(2)
    browser.expect(EC.title_contains("Example Domains"))
    assert driver.title == "Example Domains"
