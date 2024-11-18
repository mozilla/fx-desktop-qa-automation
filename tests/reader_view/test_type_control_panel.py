import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from modules.browser_object import ReaderView
from modules.page_object import GenericPage
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "130919"


size_controllers = ["minus", "plus"]
themes = [
    ("light", "rgb(255, 255, 255)"),
    ("dark", "rgb(28, 27, 34)"),
    ("sepia", "rgb(244, 236, 216)"),
    ("contrast", "rgb(0, 0, 0)"),
    ("gray", "rgb(215, 215, 219)"),
]


READER_VIEW_URL = (
    "https://support.mozilla.org/en-US/kb/firefox-reader-view-clutter-free-web-pages"
)


def test_type_control_panel_font(driver: Firefox):
    """
    C130919: Ensure the functionality of the type control panels works
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)

    web_page.open()
    reader_view.open_reader_view_searchbar()
    reader_view.click_toolbar_option("toolbar-type")

    body = web_page.get_element("page-body")

    reader_view.wait.until(
        lambda _: "sans-serif" in body.value_of_css_property("font-family")
    )
    reader_view.get_element("toolbar-font-selector").click()

    # Locate the dropdown element
    dropdown = driver.find_element(By.ID, "font-type-selector")

    # Create a Select object
    select = Select(dropdown)

    # Select the option by value
    select.select_by_value("serif")
    reader_view.wait.until(
        lambda _: "sans-serif" not in body.value_of_css_property("font-family")
        and "serif" in body.value_of_css_property("font-family")
    )


@pytest.mark.parametrize("type", size_controllers)
def test_type_control_panel_size(driver: Firefox, type: str):
    """
    C130919: Ensure the functionality of the type control panels works
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)
    util = Utilities()

    web_page.open()
    reader_view.open_reader_view_searchbar()
    reader_view.click_toolbar_option("toolbar-type")

    body = web_page.get_element("page-body")
    font_before = int(
        util.remove_all_non_numbers(body.value_of_css_property("--font-size"))
    )
    reader_view.get_element(f"toolbar-text-size-{type}").click()
    if type == "minus":
        reader_view.wait.until(
            lambda _: int(
                util.remove_all_non_numbers(body.value_of_css_property("--font-size"))
            )
            < font_before
        )
    else:
        reader_view.wait.until(
            lambda _: int(
                util.remove_all_non_numbers(body.value_of_css_property("--font-size"))
            )
            > font_before
        )


# @pytest.mark.unstable
# @pytest.mark.parametrize("type", size_controllers)
# def test_type_control_panel_width(driver: Firefox, type: str):
#     """
#     C130919: Ensure the functionality of the type control panels works
#     """
#     web_page = GenericPage(driver, url=READER_VIEW_URL)
#     reader_view = ReaderView(driver)
#     util = Utilities()
#     actions = ActionChains(driver)
#
#     web_page.open()
#     reader_view.open_reader_view_searchbar()
#     reader_view.click_toolbar_option("toolbar-type")
#
#     body = web_page.get_element("page-body")
#     width_before = int(
#         util.remove_all_non_numbers(body.value_of_css_property("--content-width"))
#     )
#
#     width_slider = reader_view.get_element("toolbar-content-width-slider")
#
#     if type == "minus":
#         actions.click_and_hold(width_slider).move_by_offset(-50, 0).release().perform()
#         reader_view.wait.until(
#             lambda _: int(
#                 util.remove_all_non_numbers(
#                     body.value_of_css_property("--content-width")
#                 )
#             )
#             < width_before
#         )
#     else:
#         actions.click_and_hold(width_slider).move_by_offset(100, 0).release().perform()
#         reader_view.wait.until(
#             lambda _: int(
#                 util.remove_all_non_numbers(
#                     body.value_of_css_property("--content-width")
#                 )
#             )
#             > width_before
#         )


# @pytest.mark.unstable
# @pytest.mark.parametrize("type", size_controllers)
# def test_type_control_panel_line_height(driver: Firefox, type: str):
#     """
#     C130919: Ensure the functionality of the type control panels works
#     """
#     web_page = GenericPage(driver, url=READER_VIEW_URL)
#     reader_view = ReaderView(driver)
#     util = Utilities()
#
#     web_page.open()
#     reader_view.open_reader_view_searchbar()
#     reader_view.click_toolbar_option("toolbar-type")
#
#     body = web_page.get_element("page-body")
#     height_before = int(
#         util.remove_all_non_numbers(body.value_of_css_property("height"))
#     )
#     reader_view.get_element(f"toolbar-line-height-{type}").click()
#     if type == "minus":
#         reader_view.wait.until(
#             lambda _: int(
#                 util.remove_all_non_numbers(body.value_of_css_property("height"))
#             )
#             < height_before
#         )
#     else:
#         reader_view.wait.until(
#             lambda _: int(
#                 util.remove_all_non_numbers(body.value_of_css_property("height"))
#             )
#             > height_before
#         )


@pytest.mark.parametrize("theme, intended_color", themes)
def test_type_control_panel_themes(driver: Firefox, theme: str, intended_color: str):
    """
    C130919: Ensure the functionality of the type control panels works
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)

    web_page.open()
    reader_view.open_reader_view_searchbar()
    reader_view.click_toolbar_option("toolbar-theme")

    body = web_page.get_element("page-body")
    reader_view.get_element(f"toolbar-theme-{theme}").click()

    reader_view.wait.until(
        lambda _: body.value_of_css_property("background-color") == intended_color
    )
