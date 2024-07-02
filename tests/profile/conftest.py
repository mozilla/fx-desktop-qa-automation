import pytest


@pytest.fixture()
def suite_id():
    return ("S2119", "Startup and Profile")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []


# path_to_profile_file = "/Users/sli/Library/Application Support/Firefox"
# path_to_profiles = "/Users/sli/Library/Application Support/Firefox/Profiles"
# path_to_profiles_ini_file = (
#     "/Users/sli/Library/Application Support/Firefox/profiles.ini"
# )
