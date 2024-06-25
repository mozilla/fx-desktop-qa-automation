from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu
from modules.page_object import ExamplePage

# def test_save_page_as(driver: Firefox):
#     pass


def test_take_screenshot(driver: Firefox):
    """
    C2637623.2: take screenshot works from context menu
    """
    # create objects
    context_menu = ContextMenu(driver)
    driver.get("https://example.com")
    example_page = ExamplePage(driver)

    # ensure that the screenshot is not present
    with driver.context(driver.CONTEXT_CHROME):
        example_page.element_does_not_exist("take-screenshot-box")

    # right click the header
    title_header = example_page.get_element("title-header")
    context_menu.context_click_element(title_header)

    # context click the screenshot option and verify its not hidden
    with driver.context(driver.CONTEXT_CHROME):
        take_screenshot = context_menu.get_context_item("context-menu-take-screenshot")
        take_screenshot.click()
        context_menu.hide_popup_by_child_node(take_screenshot)

        screenshot_box = example_page.get_element("take-screenshot-box")
        assert screenshot_box.get_attribute("hidden") is None


# def test_inspect(driver: Firefox):
#     """
#     C2637623.3: inspect works from context menu
#     """
#     # create objects
#     context_menu = ContextMenu(driver)
#     driver.get("https://example.com")
#     example_page = ExamplePage(driver)

#     # right click something that is not a hyperlink
#     title_header = example_page.get_element("title-header")
#     context_menu.context_click_element(title_header)

#     # find an element present in the dev tools
#     with driver.context(driver.CONTEXT_CHROME):
#         inspect_option = context_menu.get_context_item("context-menu-inspect")
#         inspect_option.click()
#         context_menu.hide_popup_by_child_node(inspect_option)

#         example_page.element_exists("inspect-menu-horizontal-splitter")
