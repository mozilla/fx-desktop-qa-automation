import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


@pytest.fixture()
def test_url():
    return "https://www.mozilla.com"


def test_bookmark(session, test_url):
    print(" - TEST: Verify page can be Bookmarked")
    session.get(test_url)
    WebDriverWait(session, 10).until(EC.url_changes(test_url))

    # Click Star button
    with session.context(session.CONTEXT_CHROME):
        star_button = session.find_element(By.ID, "star-button")
        star_button.click()

        # Wait for the bookmark dialog to open then Save bookmark
        save_button = WebDriverWait(session, 10).until(
            EC.presence_of_element_located((By.ID, "editBookmarkPanelDoneButton"))
        )
        save_button.click()

        # Check to confirm the Star button is filled in
        starred_value = star_button.get_attribute("starred")
        assert starred_value == "true"
        del starred_value

    # Check for the presence of the bookmark.
    with session.context(session.CONTEXT_CONTENT):
        # Open a new tab after making first tab blank
        session.get("about:blank")
        assert session.title == ""
        print(
            "The title of the page should be blank !"
            + session.title
            + "! <- Nothing between those"
        )
        session.execute_script("window.open('');")

        # Switch to the new tab and open the Mozilla URL
        session.switch_to.window(session.window_handles[1])
        session.get(test_url)
        WebDriverWait(session, 10).until(EC.url_changes("https://mozilla.com"))

    with session.context(session.CONTEXT_CHROME):
        starred_value = star_button.get_attribute("starred")
        assert starred_value == "true"
        print(
            "2nd check: The value of the starred attribute is '" + starred_value + "'"
        )
