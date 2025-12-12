import pytest
from selenium.webdriver import Firefox


@pytest.fixture()
def test_case():
    return "2804875"


def test_restore_closed_tabs_previous_groups(driver: Firefox):
    """
    C2804875 - Verify that closed tabs can be restored to their previous Groups
    """

