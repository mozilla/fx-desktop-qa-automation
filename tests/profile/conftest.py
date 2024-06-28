import pytest

from modules.util import Utilities


@pytest.fixture()
def suite_id():
    return ("S2119", "Startup and Profile")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []


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
