import random

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi


@pytest.fixture()
def use_profile():
    return "theme_change"


def trim_url(url: str) -> str:
    colon_index = url.find(":")
    if colon_index != -1:
        return url[colon_index + 1 :].strip()
    else:
        return ""


def test_open_websites_from_history(driver: Firefox):
    """
    C118807: Verify that the user can Open websites from the Toolbar History submenu
    """
    panel_ui = PanelUi(driver).open()

    panel_ui.open_history_menu()

    with driver.context(driver.CONTEXT_CHROME):
        history_items = panel_ui.get_elements("recent-history-info")
        if len(history_items) == 0:
            assert False, "There is no history."

        rand_index = random.randint(0, len(history_items) - 1)
        url_to_visit = history_items[rand_index].get_attribute("image")
        website_label = history_items[rand_index].get_attribute("label")

        trimmed_url = trim_url(url_to_visit)
    driver.get(trimmed_url)

    assert driver.current_url == trimmed_url
    assert driver.title == website_label
