import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


@pytest.fixture()
def test_url():
    return "https://example.com"


@pytest.mark.incident
def test_new_tab(driver, test_url):
    print(" - TEST: Verify a user can open a page in a new tab")

    # Navigate to an example web page
    driver.get(test_url)
    WebDriverWait(driver, 10).until(EC.url_changes("https://www.example.com/"))

    # Open another page in a new tab
    with driver.context(driver.CONTEXT_CHROME):
        newtab_button = driver.find_element(By.ID, "tabs-newtab-button")
        newtab_button.click()
        time.sleep(1)
        driver.find_element(By.ID, "urlbar-input").send_keys(
            "https://www.w3.org/People/mimasa/test/" + Keys.ENTER
        )
        time.sleep(1)

    # Verify the new page is opened
    with driver.context(driver.CONTEXT_CONTENT):
        driver.switch_to.window(driver.window_handles[1])
        WebDriverWait(driver, 10).until(EC.title_contains("Test"))
        page_title = driver.title
        assert page_title == "Test page"
        print("Title of the web page is: " + page_title)
