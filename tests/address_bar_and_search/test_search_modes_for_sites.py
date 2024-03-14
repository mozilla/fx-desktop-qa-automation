from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from modules.page_object import Navigation
from time import sleep


def test_search_modes_for_sites(driver: Firefox, search_modes: dict):
    # C2234690
    # C1365213 (potentially)
    nav = Navigation()
    wait = WebDriverWait(driver, 10)
    with driver.context(driver.CONTEXT_CHROME):
        awesome_bar = driver.find_element(*nav.awesome_bar)
        for site in search_modes["site"]:
            # For some reason Wikipedia does not elicit a search mode in automation
            if site == "Wikipedia":
                continue
            awesome_bar.send_keys(site[:2].lower())
            wait.until(EC.visibility_of_element_located(nav.tab_to_search_text_span))
            awesome_bar.send_keys(Keys.TAB)
            wait.until(EC.text_to_be_present_in_element(nav.search_mode_span, site))
            awesome_bar.send_keys("soccer" + Keys.RETURN)
            with driver.context(driver.CONTEXT_CONTENT):
                wait.until(EC.url_contains(site.lower()))
            awesome_bar.clear()
