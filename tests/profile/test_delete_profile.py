from time import sleep

from pynput.keyboard import Controller, Key
from selenium.webdriver import Firefox

from modules.page_object import AboutProfiles
from modules.util import BrowserActions, Utilities

# TODO: assign these paths based on OS
path_to_profile_file = "/Users/sli/Library/Application Support/Firefox"
path_to_profiles = "/Users/sli/Library/Application Support/Firefox/Profiles"
path_to_profiles_ini_file = (
    "/Users/sli/Library/Application Support/Firefox/profiles.ini"
)


def test_delete_profile_dont_save_files(create_profile, driver: Firefox):
    """
    C130789.1: delete the profile with the option "dont delete files"
    """

    # open firefox and proceed normally
    about_profiles = AboutProfiles(driver).open()
    sleep(20)
    # util = Utilities()
    # ba = BrowserActions(driver)
    # cannot create the profile atm : (

    # util.write_html_content("contentsbefore", driver, False)

    # about_profiles.get_element(
    #     "profile-container-item-button", labels=["profiles-remove"]
    # ).click()
    # about_profiles.create_new_profile(util, ba)

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
