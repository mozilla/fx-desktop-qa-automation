from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import Navigation


def test_search_modes_for_sites(driver: Firefox, search_modes: dict):
    # C2234690
    # C1365213 (potentially)
    nav = Navigation(driver).open()
    wait = WebDriverWait(driver, 10)
    for site in search_modes["site"]:
        # For some reason Wikipedia does not elicit a search mode in automation
        if site == "Wikipedia":
            continue
        awesome_bar = nav.set_search_mode_via_awesome_bar(site)
        awesome_bar.send_keys("soccer" + Keys.RETURN)
        with driver.context(driver.CONTEXT_CONTENT):
            wait.until(EC.url_contains(site.lower()))
        awesome_bar.clear()
