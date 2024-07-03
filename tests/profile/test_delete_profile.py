import logging
from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command

from modules.page_object import AboutProfiles
from modules.util import BrowserActions, Utilities

# TODO: assign these paths based on OS
path_to_profile_file = "/Users/sli/Library/Application Support/Firefox"
path_to_profiles = "/Users/sli/Library/Application Support/Firefox/Profiles"
path_to_profiles_ini_file = (
    "/Users/sli/Library/Application Support/Firefox/profiles.ini"
)


@pytest.fixture()
def create_profile():
    util = Utilities()
    # find the highest profile number
    profile_number = util.extract_highest_profile_number(path_to_profiles_ini_file)
    # create a new directory in the profiles dir
    new_profile_path = util.create_dir(
        path_to_profiles, f"profile{str(profile_number)}"
    )
    # append a new profile on the profiles.ini
    util.add_new_profile(path_to_profiles_ini_file, new_profile_path, profile_number)
    return f"New Profile {str(profile_number)}"


def test_delete_profile_dont_save_files(driver: Firefox):
    """
    C130789.1: delete the profile with the option "dont delete files"
    """
    # open firefox and proceed normally, get the name of the profile
    about_profiles = AboutProfiles(driver).open()
    util = Utilities()
    ba = BrowserActions(driver)
    profile_name = driver.profile_name

    profile_container = about_profiles.get_element("profile-container")
    profiles = profile_container.find_elements(By.XPATH, "./child::*")
    new_profile = None

    # find the newly created profile
    for profile in profiles:
        profile_header = about_profiles.get_element(
            "profile-container-item-profile-name", parent_element=profile
        )
        print(profile_header.get_attribute("innerHTML"))
        if profile_header.get_attribute("innerHTML") == f"Profile: {profile_name}":
            new_profile = profile
            break

    if new_profile is None:
        logging.warning("Could not find the newly made profile.")
        assert False

    # sleep(5)
    # attempt to delete the profile
    about_profiles.get_element(
        "profile-container-item-button",
        labels=["profiles-remove"],
        parent_element=new_profile,
    ).click()

    # driver.switch_to.alert

    # util.write_html_content("contents", driver, False)
    # about_profiles.get_element(
    #     "profile-container-item-button", labels=["profiles-remove"]
    # ).click()
    # about_profiles.create_new_profile(util, ba)

    alert = driver.switch_to.alert
    # sleep(10)
    driver.execute(Command.W3C_ACTIONS, {})
    # alert.send_keys("\t")
    sleep(5)
    # alert.send_keys()
    # alert.dismiss()
    # alert.accept()

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
