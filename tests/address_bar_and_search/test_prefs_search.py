from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.page_object import AboutPrefs


def test_search_prefs(driver: Firefox):
    about_prefs = AboutPrefs(driver, category="general").open()
    about_prefs.find_in_settings("pri")
    about_prefs.expect(
        EC.visibility_of_element_located(
            about_prefs.get_selector("h2-enhanced-tracking-protection")
        )
    )
