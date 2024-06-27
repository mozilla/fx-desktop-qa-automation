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

    # util.write_html_content("contentsbefore", driver, False)

    # about_profiles.get_element(
    #     "profile-container-item-button", labels=["profiles-remove"]
    # ).click()
    about_profiles.create_new_profile(util, ba)

    # alert = driver.switch_to.alert
    # sleep(10)
    # alert.accept()
    # util.write_html_content("contentsafter", driver, False)

    # ba.key_press_release(Key.tab)
    # print("hello")
    # ba.key_press_release(Key.tab)
    # print('hello')
    # ba.key_press_release(Key.tab)
    # print('hello')
    # ba.key_press_release(Key.tab)
    # print('hello')
    # ba.key_press_release(Key.tab)
    # sleep(10)


# def test_delete_profile_delete_files(driver: Firefox):
#     """
#     C130789.2: delete the profile with the option "delete files"
#     """
