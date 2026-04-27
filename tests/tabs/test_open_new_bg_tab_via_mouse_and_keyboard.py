import pytest
from selenium.webdriver import Firefox

from modules.page_object import ExamplePage

TEST_URL = "https://www.iana.org/help/example-domains"


@pytest.fixture()
def test_case():
    return "134455"


@pytest.mark.headed
def test_open_new_bg_tab_via_mouse_and_keyboard(driver: Firefox):
    """
    C134455 - Verify that opening hyperlink with mouse or keyboard
    shortcuts creates new background tabs
    """

    # Instantiate objects
    example = ExamplePage(driver)
    example.open()

    # Middle click link, verify new background tab opens with correct URL
    example.middle_click("learn-more")
    example.wait_for_num_tabs(2)
    example.switch_to_new_tab()

    assert driver.current_url == TEST_URL

    # Close new tab, switch back to original example page
    driver.close()
    example.switch_to_new_tab()

    # Control click link, verify new background tab opens with correct URL
    example.control_click("learn-more")
    example.wait_for_num_tabs(2)
    example.switch_to_new_tab()

    assert driver.current_url == TEST_URL
