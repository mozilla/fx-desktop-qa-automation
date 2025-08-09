import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.page_object import ExamplePage


@pytest.fixture()
def test_case():
    return "134455"


@pytest.mark.headed
def test_open_new_bg_tab_via_mouse_and_keyboard(driver: Firefox):
    """
    C134455 - Verify that opening hyperlink with mouse or keyboard
    shortcuts creates new background tabs
    """

    test_url = "https://www.iana.org/help/example-domains"
    example = ExamplePage(driver).open()

    # Middle click link, verify new background tab opens with correct URL
    example.middle_click("more-information")
    example.wait_for_num_tabs(2)
    example.switch_to_new_tab()

    assert driver.current_url == test_url

    # Close new tab, switch back to original example page
    driver.close()
    example.switch_to_new_tab()

    # Control click link, verify new background tab opens with correct URL
    example.control_click("more-information")
    example.wait_for_num_tabs(2)
    example.switch_to_new_tab()

    assert driver.current_url == test_url