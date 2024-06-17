from time import sleep

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

    # ensure not initially set to default
    table_rows = about_profiles.get_element(
        "profile-container-item-table-row", multiple=True
    )
    # row 0 contains the default profile information
    first_row_default_profile_value = about_profiles.get_element(
        "profile-container-item-table-row-value", parent_element=table_rows[0]
    ).get_attribute("data-l10n-id")
    # assert first_row_default_profile_value == "profiles-no"
    sleep(5)

    # First profile is not the default, set to default
    # about_profiles.get_element("profile-container-item-button", parent_element=first_profile, labels=["profiles-set-as-default"]).click()

    # # refetch items to ensure freshnesss
    # table_rows = about_profiles.get_element("profile-container-item-table-row", multiple=True)
    # first_row_default_profile_value = about_profiles.get_element("profile-container-item-table-row-value", parent_element=table_rows[0]).get_attribute("data-l10n-id")
    # print(first_row_default_profile_value)

    # about_profiles.get_element("profile-container-item-button", parent_element=second_profile, labels=["profiles-set-as-default"]).click()
