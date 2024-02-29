import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


@pytest.fixture()
def test_url():
    return "https://www.twitch.com"


def test_twitch_search(driver, test_url):
    print(" - TEST: Verify a user can search on Twitch")

    # Navigate to Twitch
    driver.get(test_url)
    WebDriverWait(driver, 10).until(EC.url_contains("https://www.twitch.tv"))

    # Verify the Twitch page is loaded
    WebDriverWait(driver, 10).until(EC.title_contains("Twitch"))
    page_title = driver.title
    assert page_title == "Twitch"
    print("Title of the web page is: " + page_title)

    # Find the search input field and enter "Diablo IV"
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[aria-label="Search Input"]')
        )
    )
    search_input.send_keys("Diablo IV")
    search_input.send_keys(Keys.RETURN)

    # Wait for the search results to load
    item_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                ".kEZcIh > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > "
                "div:nth-child(1) > strong:nth-child(1) > a:nth-child(1)",
            )
        )
    )
    item_element_text = item_element.text
    print("Element found by CSS:", item_element_text)
    assert "Diablo" in item_element_text
