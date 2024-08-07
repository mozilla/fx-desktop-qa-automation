from time import sleep
import logging
import pytest
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

from modules.browser_object import TabBar
from modules.util import Utilities

# util = Utilities()
# temp_profile_path = util.create_temp_profile()
#
# # Set up the Firefox options and set the profile
# options = webdriver.FirefoxOptions()
# options.profile = temp_profile_path
#
# # Initialize the Firefox driver with the temporary profile
# FirefoxDriver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

util = Utilities()


@pytest.fixture
def firefox_driver():
    """
    C134453 - A new tab can be opened from the dedicated button ("+")
    """
    temp_profile_path = util.create_temp_profile()
    logging.info("Temp profile path is:" + temp_profile_path)

    # Set up the Firefox options and set the profile
    options = webdriver.FirefoxOptions()
    options.profile = temp_profile_path

    # Initialize the Firefox driver with the temporary profile
    fxdriver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

    yield fxdriver
    # Close the browser
    fxdriver.quit()
    # driver.quit()
    # Removed the temp profile
    util.remove_temp_profile(temp_profile_path)


def test_open_new_tab_plus(firefox_driver):
    fxdriver = firefox_driver
    # tab_browser = TabBar(driver).open()
    tab_browser = TabBar(fxdriver)
    fxdriver.get("about:robots")
    tab_browser.set_chrome_context()
    tab_browser.new_tab_by_button()
    tab_browser.expect(EC.title_contains("Mozilla Firefox"))
    assert fxdriver.title == "Mozilla Firefox"
