import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


@pytest.fixture()
def test_url():
    return "https://www.mozilla.com"


@pytest.mark.incident
def test_bookmark(driver, test_url):
    print(" - TEST: Verify page can be Bookmarked")
    driver.get(test_url)
    WebDriverWait(driver, 10).until(EC.url_changes(test_url))

    # Click Star button
    with driver.context(driver.CONTEXT_CHROME):
        star_button = driver.find_element(By.ID, "star-button")
        star_button.click()

        # Wait for the bookmark dialog to open then Save bookmark
        save_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "editBookmarkPanelDoneButton"))
        )
        save_button.click()

        # Check to confirm the Star button is filled in
        starred_value = star_button.get_attribute("starred")
        assert starred_value == "true"
        del starred_value

    # Check for the presence of the bookmark.
    with driver.context(driver.CONTEXT_CONTENT):
        # Open a new tab after making first tab blank
        driver.get("about:blank")
        assert driver.title == ""
        print(
            "The title of the page should be blank !"
            + driver.title
            + "! <- Nothing between those"
        )
        driver.execute_script("window.open('');")

        # Switch to the new tab and open the Mozilla URL
        driver.switch_to.window(driver.window_handles[1])
        driver.get(test_url)
        WebDriverWait(driver, 10).until(EC.url_changes("https://mozilla.com"))

    with driver.context(driver.CONTEXT_CHROME):
        starred_value = star_button.get_attribute("starred")
        assert starred_value == "true"
        print(
            "2nd check: The value of the starred attribute is '" + starred_value + "'"
        )
