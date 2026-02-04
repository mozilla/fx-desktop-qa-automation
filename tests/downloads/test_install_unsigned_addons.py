import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage

TEST_URL = (
    "https://drive.google.com/file/d/1XgNzc9QM-QNLZQcha-qtbAtAdd5iyTHk/view?hl=en"
)


@pytest.fixture()
def delete_files_regex_string():
    return r"tomato_clock-6.0.2.xpi"


@pytest.fixture()
def test_case():
    return "1781220"


@pytest.fixture()
def add_to_prefs_list():
    return [("xpinstall.signatures.required", False)]


def test_install_unsigned_addons(driver: Firefox):
    """
    C1781220 - Verify that the user can install unsigned add-ons
    """

    # Instantiate objects
    page = GenericPage(driver, url=TEST_URL)
    nav = Navigation(driver)

    # Install the following unsigned add-on
    page.open()
    page.click_on("gdoc-download-addon")

    # The unsigned add-on is successfully installed.
    nav.element_visible("xpi-download-target-element")
