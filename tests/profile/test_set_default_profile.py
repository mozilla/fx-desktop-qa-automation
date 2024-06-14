from time import sleep

from selenium.webdriver import Firefox

from modules.page_object import AboutProfiles


def test_set_default_profile(driver: Firefox):
    """
    C130792, set the default profile through the firefox browser
    """
    about_profiles = AboutProfiles(driver).open()
    sleep(10)
