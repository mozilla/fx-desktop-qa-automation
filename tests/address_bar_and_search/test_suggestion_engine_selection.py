import time

import pytest
from selenium.webdriver import Firefox, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import Navigation

sites = ["Google", "Amazon.com", "Bing", "DuckDuckGo", "eBay"]


@pytest.mark.parametrize("site", sites)
def test_search_suggestion_for_engine_selection(driver: Firefox, site: str):
    nav = Navigation(driver).open()
    nav.type_in_awesome_bar("@")

    # Try to find the element multiple times with a small delay between each attempt
    for _ in range(30):
        try:
            suggestion_list_items = nav.get_elements("search-suggestion-list")
            if suggestion_list_items:
                break  # If the elements are found, break out of the loop
        except Exception:
            pass
        time.sleep(1)  # If the elements are not found, wait for a second and try again

    # Filter elements to find the one that matches the desired site
    suggestion_list_item = next(
        (item for item in suggestion_list_items if site in item.text), None
    )

    if suggestion_list_item:
        suggestion_list_item.click()
        nav.type_in_awesome_bar("cobra" + Keys.ENTER)
        nav.expect_in_content(EC.url_contains(site.lower()))
    else:
        pytest.fail(f"No search suggestion found for site: {site}")

    nav.clear_awesome_bar()
