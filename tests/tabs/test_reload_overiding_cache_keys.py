import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from modules.browser_object import TabBar


@pytest.fixture()
def test_case():
    return "134642"


TEST_URL = "https://postman-echo.com/headers"


def test_reload_overiding_cache_keys(driver: Firefox, sys_platform: str):
    """
    C134642 - Verify that tabs can be hard reloaded (overriding cache) using keyboard shortcut CTRL/CMD + SHIFT + R.
    """

    browser = TabBar(driver)

    # New tab + navigate
    browser.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(TEST_URL)

    # Hard reload action sequence hold CTRL/CMD + SHIFT and press "r"
    with driver.context(driver.CONTEXT_CHROME):
        actions = browser.actions
        if sys_platform == "Darwin":
            actions.key_down(Keys.COMMAND).key_down(Keys.SHIFT).send_keys("r").key_up(
                Keys.SHIFT
            ).key_up(Keys.COMMAND).perform()
        else:
            actions.key_down(Keys.CONTROL).key_down(Keys.SHIFT).send_keys("r").key_up(
                Keys.SHIFT
            ).key_up(Keys.CONTROL).perform()

    # Verify cache is not being used by checking for http request headers
    # Header "if-none-match" should not be sent
    try:
        etag = driver.find_element(By.ID, "/headers/if-none-match").get_attribute(
            "innerText"
        )
        assert False, f"Unexpected If-None-Match present: {etag!r}"
    except NoSuchElementException:
        pass

    # Header "pragma" should be sent with with value "no-cache"
    pragma_text = driver.find_element(By.ID, "/headers/pragma").get_attribute(
        "innerText"
    )
    assert "no-cache" in pragma_text, (
        f"Expected 'no-cache' in pragma; got: {pragma_text!r}"
    )

    # Header "cache-control" should be sent with with value "no-cache"
    cache_control_text = driver.find_element(
        By.ID, "/headers/cache-control"
    ).get_attribute("innerText")
    assert "no-cache" in cache_control_text, (
        f"Expected 'no-cache' in cache-control; got: {cache_control_text!r}"
    )
