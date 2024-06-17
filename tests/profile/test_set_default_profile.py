import logging
from time import sleep

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.page_object import AboutProfiles


def test_set_default_profile(driver: Firefox):
    """
    C130792, set the default profile through the firefox browser
    """
    about_profiles = AboutProfiles(driver).open()

    profiles_div = about_profiles.get_element("profile-container")

    child_elements = profiles_div.find_elements(By.XPATH, "./child::*")
    default_profile_element = child_elements[0]
    default_profile_element.find_element(
        By.CSS_SELECTOR, "h3[data-l10n-id='profiles-in-use-profile']"
    )
