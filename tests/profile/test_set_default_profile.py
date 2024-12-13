import logging
import os
import tempfile
from shutil import rmtree
from zipfile import ZipFile 

import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutProfiles


@pytest.fixture()
def test_case():
    return "130792"


@pytest.fixture()
def profile_paths():
    return ["profiles/theme_change.zip", "profiles/theme_change_dup.zip"]


@pytest.fixture()
def create_profiles(profile_paths, opt_ci, sys_platform):
    """
    Creates profiles that will be recognised in about:profiles
    """
    # Extracts the provided profiles into a temporary location
    tmpdir = []
    for i in range(len(profile_paths)):
        tmpdirname = tempfile.mkdtemp()
        with ZipFile(profile_paths[i], 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)
            logging.info(f"{profile_paths[i]} contents are extracted to temp dir {tmpdirname}")
            tmpdir.append(tmpdirname)

    # Add the extracted profiles to profile.ini
    profile_loc = {
        "Windows": os.path.join(os.getenv("APPDATA", ""), "Mozilla", "Firefox"),
        "Darwin": os.path.expanduser(r"~/Library/Application Support/Firefox"),
        "Linux": os.path.expanduser(r"~/.mozilla/firefox")
    }
    num_profiles = 0
    profile_file = os.path.join(profile_loc[sys_platform], "profiles.ini")

    try:
        file_size = os.stat(profile_file).st_size
        with open(profile_file, "r") as p:
            num_profiles += sum(1 for line in p if line.startswith("[Profile"))
    except Exception:
        file_size = 0

    with open(profile_file, "a") as p:
        for i in range(len(tmpdir)):
            p.write("\n")
            p.write(f"[Profile{num_profiles}]\n")
            p.write(f"Name=test{num_profiles}\n")
            p.write("IsRelative=0\n")
            p.write(f"Path={tmpdir[i]}\n")
            num_profiles += 1

    yield

    # Clean up the created directories
    for dir in tmpdir:
        rmtree(dir)
        logging.info(f"temp dir {dir} is deleted")

    # Clean up profiles.ini
    if file_size:
        with open(profile_file, "a") as p:
            p.truncate(file_size)
            logging.info(f"removing added profiles from profiles.ini")
    else:
        os.remove(profile_file)


def test_set_default_profile(driver: Firefox, opt_ci):
    """
    C130792: Set the default profile through the firefox browser
    """
    about_profiles = AboutProfiles(driver)

    # Get the profiles container, extract all relevant children under it.
    about_profiles.open()
    profiles = about_profiles.get_all_children("profile-container")

    # Find index that is the current default
    cur_default = -1
    for i in range(len(profiles)):
        logging.info(f"Currently searching row {i} for the default profile")
        cur_profile = profiles[i]
        table_rows = about_profiles.get_element(
            "profile-container-item-table-row",
            multiple=True,
            parent_element=cur_profile,
        )
        # Find the current default profile
        default_profile_information = about_profiles.get_element(
            "profile-container-item-table-row-value", parent_element=table_rows[0]
        )
        if default_profile_information.get_attribute("innerHTML") == "yes":
            logging.info(f"Found the default profile at {i}!")
            cur_default = i
            break

    # Set test profile as the default and verify the rows
    logging.info(f"Preparing to set test profile to the default.")
    about_profiles.get_element(
        "profile-container-item-button",
        parent_element=profiles[-1],
        labels=["profiles-set-as-default"],
    ).click()

    # Refetch data to ensure no stale elements
    profiles = about_profiles.get_all_children("profile-container")

    table_rows = about_profiles.get_element(
        "profile-container-item-table-row",
        multiple=True,
        parent_element=profiles[-1],
    )
    about_profiles.wait.until(
        lambda _: about_profiles.get_element("profile-container-item-table-row-value", parent_element=table_rows[0])
        .get_attribute("innerHTML") == "yes"
        )
    logging.info(f"Verified that test profile was set to the default.")

    # Set the previous default back to default
    if not opt_ci:
        logging.info(f"Preparing to set profile {cur_default} to the default.")
        original_default = profiles[cur_default]
        about_profiles.get_element(
            "profile-container-item-button",
            parent_element=original_default,
            labels=["profiles-set-as-default"],
        ).click()
