from time import sleep

from pynput.keyboard import Controller, Key
from selenium.webdriver import Firefox

from modules.page_object import AboutProfiles
from modules.util import BrowserActions, Utilities


def test_delete_profile_dont_save_files(driver: Firefox):
    """
    C130789.1: delete the profile with the option "dont delete files"
    """
    about_profiles = AboutProfiles(driver).open()
    util = Utilities()
    ba = BrowserActions(driver)
    # cannot create the profile atm : (
    # about_profiles.create_new_profile(util, ba)

    about_profiles.get_element(
        "profile-container-item-button", labels=["profiles-remove"]
    ).click()

    ba.key_press_release(Key.tab)
    ba.key_press_release(Key.tab)
    ba.key_press_release(Key.tab)
    ba.key_press_release(Key.tab)
    ba.key_press_release(Key.tab)
    sleep(10)


# def test_delete_profile_delete_files(driver: Firefox):
#     """
#     C130789.2: delete the profile with the option "delete files"
#     """
