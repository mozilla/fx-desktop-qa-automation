from collections.abc import Callable

import pytest
from selenium.webdriver import ActionChains, Firefox
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from modules.page_object import ExamplePage

TEST_URL = "https://www.iana.org/help/example-domains"
LINK_ELEMENT = "learn-more"
TAB_OPEN_TIMEOUT = 10


@pytest.fixture()
def test_case():
    return "134455"


def _middle_click(driver: Firefox, element: WebElement) -> None:
    """Middle-click an element using W3C pointer actions."""
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    actions.w3c_actions.pointer_action.pointer_down(1)
    actions.w3c_actions.pointer_action.pointer_up(1)
    actions.perform()


def _verify_link_opens_in_background(
    driver: Firefox,
    example: ExamplePage,
    click_action: Callable[[WebElement], object],
) -> None:
    original_handle = driver.current_window_handle
    handles_before = set(driver.window_handles)

    try:
        example.element_clickable(LINK_ELEMENT)
        link = example.get_element(LINK_ELEMENT)
        click_action(link)

        def _new_tab_handle(current_driver):
            new_handles = set(current_driver.window_handles) - handles_before

            if len(new_handles) == 1:
                return next(iter(new_handles))

            return False

        new_handle = WebDriverWait(driver, TAB_OPEN_TIMEOUT).until(_new_tab_handle)

        assert driver.current_window_handle == original_handle, (
            "Expected the link to open in a background tab"
        )

        driver.switch_to.window(new_handle)
        example.url_contains(TEST_URL)

    finally:
        for handle in set(driver.window_handles) - handles_before:
            driver.switch_to.window(handle)
            driver.close()

        if original_handle in driver.window_handles:
            driver.switch_to.window(original_handle)


@pytest.mark.headed
def test_open_new_bg_tab_via_mouse_and_keyboard(driver: Firefox):
    """
    C134455 - Verify that opening hyperlink with mouse or keyboard
    shortcuts creates new background tabs
    """
    example = ExamplePage(driver)
    example.open()

    # Verify opening the link with a W3C middle click.
    _verify_link_opens_in_background(
        driver,
        example,
        lambda link: _middle_click(driver, link),
    )

    # Verify opening the link with Control/Command click.
    _verify_link_opens_in_background(
        driver,
        example,
        example.control_click,
    )
