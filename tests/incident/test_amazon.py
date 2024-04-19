# This test searches for a soccer ball on Amazon.
#  It can fails after a while due to bot identification by Amazon

import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


@pytest.fixture()
def test_url():
    return "https://www.amazon.com"


def test_amazon_search(driver, test_url):
    print(" - TEST: Verify a user can search on Amazon")

    # Remove navigator.webdriver Flag using JavaScript to avoid bot detection by Amazon
    # NOTE: This worked for a while, then it intermittently stops working and Amazon Captcha got us again.
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    driver.get(test_url)
    WebDriverWait(driver, 10).until(EC.url_contains("https://www.amazon.com"))

    # Verify the Amazon page is loaded
    WebDriverWait(driver, 10).until(EC.title_is("Amazon.com. Spend less. Smile more."))

    # Find the search input field and enter "soccer ball"
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
    )
    time.sleep(2)
    search_input.send_keys("soccer ball", Keys.RETURN)

    # Wait for the search results to load
    item_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//html/body/div[1]/div[1]/span[2]/div/h1/div/div[1]/div/div/span[3]",
            )
        )
    )
    item_element_text = item_element.text
    print("Element found by class name:", item_element_text)
    assert "soccer ball" in item_element_text
