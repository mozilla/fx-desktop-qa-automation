import time

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.page_object import AboutPrefs, Navigation
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "936860"


URL_TO_VISIT = "https://en.wikipedia.org/wiki/Mozilla"

def test_zoom_text_only_from_prefs(driver: Firefox):
    # Initializing objects
    about_prefs = AboutPrefs(driver, category="General").open()

    about_prefs.click_on("zoom-text-only")
    time.sleep(5)
    about_prefs.click_on("zoom-level")
    
    with driver.context(driver.CONTEXT_CHROME):
        about_prefs.get_element("zoom-level-choice").click()

        
    time.sleep(3)
    

    # about_prefs.actions.send_keys(Keys.DOWN, Keys.ENTER)
    time.sleep(10)

