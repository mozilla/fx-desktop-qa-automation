import pytest
from selenium.webdriver import Firefox


@pytest.fixture()
def test_case():
    return "2264690"


def test_about_logins_copy_prompts_primary_password(driver: Firefox):
    """
    C2264690 - Verify that clicking the 'Copy' password button prompts for the Primary Password before copying the password
    """