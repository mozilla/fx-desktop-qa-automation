
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.fixture()
def test_url():
    return "https://example.com"


def test_new_tab(session, test_url):
    print(" - TEST: Verify a user can open a page in a new tab")

    # Navigate to an example web page
    session.get(test_url)
    WebDriverWait(session, 10).until(EC.url_changes('https://www.example.com/'))

    # Open another page in a new tab
    with session.context(session.CONTEXT_CHROME):
        newtab_button = session.find_element(By.ID, "tabs-newtab-button")
        newtab_button.click()
        time.sleep(1)
        session.find_element(By.ID, 'urlbar-input').send_keys(
            "https://www.w3.org/People/mimasa/test/" + Keys.ENTER)
        time.sleep(1)

    # Verify the new page is opened
    with session.context(session.CONTEXT_CONTENT):
        session.switch_to.window(session.window_handles[1])
        WebDriverWait(session, 10).until(EC.title_contains('Test'))
        page_title = session.title
        assert page_title == "Test page"
        print("Title of the web page is: " + page_title)
