import logging
import random

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.page_object import AboutProfiles


def test_set_default_profile(driver: Firefox):
    """
    C130792, set the default profile through the firefox browser
    """
    about_profiles = AboutProfiles(driver).open()

    # get the profiles container, extract all relevant children under it.
    profile_container = about_profiles.get_element("profile-container")
    profiles = profile_container.find_elements(By.XPATH, "./child::*")

    # verify first item has the bold text
    first_profile = profiles[0]
    # second_profile = profiles[1]
    first_profile_header = about_profiles.get_element(
        "profile-container-item-default-header", parent_element=first_profile
    )
    assert first_profile_header is not None

    cur_default = -1

    # find index that is the current default
    for i in range(len(profiles)):
        logging.info(f"Currently searching row {i} for the default profile")
        cur_profile = profiles[i]
        table_rows = about_profiles.get_element(
            "profile-container-item-table-row",
            multiple=True,
            parent_element=cur_profile,
        )
        first_row = table_rows[0]
        # find the current default profile
        default_profile_information = about_profiles.get_element(
            "profile-container-item-table-row-value", parent_element=first_row
        )
        if default_profile_information.get_attribute("innerHTML") == "yes":
            logging.info(f"Found the default profile at {i}!")
            cur_default = i
            break

    # no default profile could be found
    if cur_default == -1:
        logging.warn("Could not find a currently active default profile.")
        assert False

    # select a non default profile randomly
    profile_index = random.randint(0, len(profiles) - 1)
    if profile_index == cur_default:
        profile_index = random.randint(0, len(profiles) - 1)

    # set it as the default and verify the rows
    logging.info(f"Preparing to set profile {profile_index} to the default.")
    about_profiles.get_element(
        "profile-container-item-button",
        parent_element=profiles[profile_index],
        labels=["profiles-set-as-default"],
    ).click()

    # refetch data to ensure no stale elements
    profile_container = about_profiles.get_element("profile-container")
    profiles = profile_container.find_elements(By.XPATH, "./child::*")

    table_rows = about_profiles.get_element(
        "profile-container-item-table-row",
        multiple=True,
        parent_element=profiles[profile_index],
    )
    default_profile_information = about_profiles.get_element(
        "profile-container-item-table-row-value", parent_element=table_rows[0]
    )
    assert default_profile_information.get_attribute("innerHTML") == "yes"
    logging.info(f"Verified that profile {profile_index} was set to the default.")

    # set the previous default back to default
    logging.info(f"Preparing to set profile {cur_default} to the default.")
    original_default = profiles[cur_default]
    about_profiles.get_element(
        "profile-container-item-button",
        parent_element=original_default,
        labels=["profiles-set-as-default"],
    ).click()
