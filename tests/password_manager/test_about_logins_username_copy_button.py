import pytest
from selenium.webdriver import Firefox


@pytest.fixture()
def test_case():
    return "2241090"


def test_about_logins_username_copy_button(driver: Firefox):
    """
    C2241090 - Verify that Username "Copy" button functions correctly
    """

    # Instantiate objects
