import logging
import os
import shutil

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from modules.page_object import AboutProfiles
from modules.util import Utilities

# TODO: assign these paths based on OS
path_to_profile_file = "/Users/sli/Library/Application Support/Firefox"
path_to_profiles = "/Users/sli/Library/Application Support/Firefox/Profiles"
path_to_profiles_ini_file = (
    "/Users/sli/Library/Application Support/Firefox/profiles.ini"
)

# take util helper into profile pom
# make fixture for the profile path
# add try finally for cleanup


@pytest.fixture()
def create_profile():
    util = Utilities()
    # find the highest profile number
    profile_number = util.extract_highest_profile_number(path_to_profiles_ini_file)
    # create a new directory in the profiles dir
    new_profile_path = util.create_dir(
        path_to_profiles, f"profile{str(profile_number)}"
    )
    # create a copy of the profiles.ini to make restoration easy
    util.create_file_copy(
        path_to_profiles_ini_file, f"{path_to_profile_file}/profilescopy.ini"
    )
    # append a new profile on the profiles.ini
    util.add_new_profile(path_to_profiles_ini_file, new_profile_path, profile_number)
    # return profile_number
    return profile_number


def test_delete_profile_dont_save_files(driver: Firefox):
    """
    C130789.1: delete the profile with the option "dont delete files"
    """
    try:
        # open firefox and proceed normally, get the name of the profile
        about_profiles = AboutProfiles(driver).open()
        profile_number = driver.profile_number

        profile_container = about_profiles.get_element("profile-container")
        profiles = profile_container.find_elements(By.XPATH, "./child::*")
        new_profile = None

        # find the newly created profile
        for profile in profiles:
            profile_header = about_profiles.get_element(
                "profile-container-item-profile-name", parent_element=profile
            )
            print(profile_header.get_attribute("innerHTML"))
            if (
                profile_header.get_attribute("innerHTML")
                == f"Profile: New Profile {str(profile_number)}"
            ):
                new_profile = profile
                break

        if new_profile is None:
            logging.warning("Could not find the newly made profile.")
            assert False

        # attempt to delete the profile
        about_profiles.get_element(
            "profile-container-item-button",
            labels=["profiles-remove"],
            parent_element=new_profile,
        ).click()

        # switch to the alert and accept it (dont delete files)
        about_profiles.expect(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.accept()

        # verify that local files were not deleted
        if os.path.isdir(f"{path_to_profiles}/profile{str(profile_number)}"):
            logging.info(
                f"The directory '{path_to_profiles}/profile{str(profile_number)}' exists."
            )
        else:
            assert False, f"The directory '{path_to_profiles}/profile{str(profile_number)}' does not exist."

    # relevant file system cleanup
    finally:
        # delete the profile directory
        try:
            # basically rm -rf. very dangerous, stay cautious of the path
            shutil.rmtree(f"{path_to_profiles}/profile{str(profile_number)}")
        except Exception as e:
            logging.warning(f"Could not remove the profile directory: {e}")

        # delete the profiles.ini file
        try:
            os.remove(path_to_profiles_ini_file)
        except Exception as e:
            logging.warning(f"Could not delete the modified profiles.ini file. {e}")

        # rename the profilescopy.ini file to profiles.ini
        try:
            os.rename(
                f"{path_to_profile_file}/profilescopy.ini", path_to_profiles_ini_file
            )
        except Exception as e:
            logging.warning(f"Could not rename the copy of profiles.ini. {e}")
