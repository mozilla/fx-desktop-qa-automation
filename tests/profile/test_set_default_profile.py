import logging
import time
from pynput.keyboard import Controller, Key

import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutProfiles


@pytest.fixture()
def test_case():
    return "130792"


@pytest.mark.headed
def test_set_default_profile(driver: Firefox, opt_ci):
    """
    C130792, set the default profile through the firefox browser
    """
    about_profiles = AboutProfiles(driver)
    keyboard = Controller()

    # Create two profiles as CI does not have profiles
    about_profiles.open()
    for i in range(2):
        about_profiles.click_on("create-new-profile")
        time.sleep(1)
        keyboard.tap(Key.enter)
        keyboard.type(f"user{i}")
        keyboard.tap(Key.enter)

    # Get the profiles container, extract all relevant children under it.
    profiles = about_profiles.get_all_children("profile-container")

    # Verify that some profile is the default
    about_profiles.wait.until(
        lambda _: about_profiles.get_element("profile-container-item-default-header") is not None
        )

    cur_default = -1

    # Find index that is the current default
    for i in range(len(profiles)):
        logging.info(f"Currently searching row {i} for the default profile")
        cur_profile = profiles[i]
        table_rows = about_profiles.get_element(
            "profile-container-item-table-row",
            multiple=True,
            parent_element=cur_profile,
        )
        first_row = table_rows[0]
        # Find the current default profile
        default_profile_information = about_profiles.get_element(
            "profile-container-item-table-row-value", parent_element=first_row
        )
        if default_profile_information.get_attribute("innerHTML") == "yes":
            logging.info(f"Found the default profile at {i}!")
            cur_default = i
            break

    # No default profile could be found
    if cur_default == -1:
        logging.warning("Could not find a currently active default profile.")
        assert False

    # Select a non default profile randomly
    profile_indices = [i for i in range(len(profiles)) if i != cur_default]
    profile_index = random.choice(profile_indices)

    # Set it as the default and verify the rows
    logging.info(f"Preparing to set profile {profile_index} to the default.")
    about_profiles.get_element(
        "profile-container-item-button",
        parent_element=profiles[profile_index],
        labels=["profiles-set-as-default"],
    ).click()

    # Refetch data to ensure no stale elements
    profiles = about_profiles.get_all_children("profile-container")

    table_rows = about_profiles.get_element(
        "profile-container-item-table-row",
        multiple=True,
        parent_element=profiles[profile_index],
    )
    about_profiles.wait.until(
        lambda _: about_profiles.get_element("profile-container-item-table-row-value", parent_element=table_rows[0])
        .get_attribute("innerHTML") == "yes"
        )
    logging.info(f"Verified that profile {profile_index} was set to the default.")

    # Set the previous default back to default
    logging.info(f"Preparing to set profile {cur_default} to the default.")
    original_default = profiles[cur_default]
    about_profiles.get_element(
        "profile-container-item-button",
        parent_element=original_default,
        labels=["profiles-set-as-default"],
    ).click()

    # Remove the created profiles
    if opt_ci:
        pass
