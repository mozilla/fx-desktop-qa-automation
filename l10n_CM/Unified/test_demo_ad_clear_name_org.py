import pytest
from selenium.webdriver import Firefox


@pytest.fixture()
def test_case():
    return "2888560"


def test_demo_ad_clear_name_org(driver: Firefox, region: str):
    """
    C2888560 - Verify clear functionality after selecting an entry from name/org fields
    """