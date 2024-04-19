# This test searches for soccer tricks on TikTok.
# Test is blocked by TikTok login

import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


@pytest.fixture()
def test_url():
    return "https://www.tiktok.com"


@pytest.mark.incident
@pytest.mark.skip("Test blocked by login and puzzle captcha")
def test_new_tab(driver, test_url):
    print(" - TEST: Verify a user can search on TikTok")
    # Remove navigator.webdriver Flag using JavaScript to avoid bot detection by TikTok
    # NOTE: This doesn't work. TikTok has a puzzle piece captcha against search results.
    # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # Navigate to TikTok
    driver.get(test_url)
    WebDriverWait(driver, 10).until(EC.url_contains("https://www.tiktok.com"))

    # Verify the TikTok page is loaded
    WebDriverWait(driver, 10).until(EC.title_contains("videos on TikTok"))
    page_title = driver.title
    assert page_title == "Explore - Find your favourite videos on TikTok"
    print("Title of the web page is: " + page_title)

    # Find the search input field and enter "soccer tricks"
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']"))
    )
    time.sleep(2)
    search_input.send_keys("soccer tricks", Keys.RETURN)

    # Wait for the search results to load
    item_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//div[1]/div[2]/div[2]/div[1]/div[2]/div/div[1]/a[2]/p[2]/strong",
            )
        )
    )
    item_element_text = item_element.text
    print("Element found by class name:", item_element_text)
    assert "Soccer trick" in item_element_text
