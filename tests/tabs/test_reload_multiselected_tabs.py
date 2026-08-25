from shutil import copyfile

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import ContextMenu, Navigation, TabBar

RELOAD_SELECTED_TABS = "context-menu_reload-selected-tabs"

# One local page per tab
PAGE_FILENAMES = [
    "basic_webpage.html",
    "article_page.html",
    "mp3_download.html",
    "web_audio_landing.html",
]

# Indices of those tabs, 1-based
SELECTED_TAB_INDICES = [2, 3, 4, 5]


@pytest.fixture()
def test_case():
    return "4038574"


@pytest.fixture()
def page_urls(tmp_path):
    """Copy the test pages to tmp_path and return their file:// URLs"""
    for filename in PAGE_FILENAMES:
        copyfile(f"data/pages/{filename}", tmp_path / filename)
    return [f"file://{tmp_path / filename}" for filename in PAGE_FILENAMES]


def get_time_origins(driver: Firefox, handles: list[str]) -> dict[str, float]:
    """Return the page time origin of every given tab"""
    time_origins = {}
    for handle in handles:
        driver.switch_to.window(handle)
        time_origins[handle] = driver.execute_script("return performance.timeOrigin")
    return time_origins


def verify_tabs_reloaded(
    driver: Firefox, tabs: TabBar, time_origins: dict[str, float]
) -> None:
    """A new page time origin means the tab reloaded"""
    for handle, previous_time_origin in time_origins.items():
        driver.switch_to.window(handle)
        tabs.expect_in_content(
            lambda d, previous=previous_time_origin: d.execute_script(
                "return performance.timeOrigin"
            )
            != previous
        )


def test_reload_multiselected_tabs(
    driver: Firefox, sys_platform: str, page_urls: list[str]
):
    """
    C4038574 - Verify that multiselected tabs can be reloaded
    """

    tabs = TabBar(driver)
    nav = Navigation(driver)
    tab_context_menu = ContextMenu(driver)

    mod_key = Keys.COMMAND if sys_platform == "Darwin" else Keys.CONTROL

    # Step 1: Open more than 3 tabs with different webpages
    for url in page_urls:
        tabs.new_tab_by_button()
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(url)

    assert len(driver.window_handles) == len(PAGE_FILENAMES) + 1
    page_handles = driver.window_handles[1:]

    # Step 2: Multiselect the tabs and reload via the toolbar button
    time_origins = get_time_origins(driver, page_handles)
    tabs.select_multiple_tabs_by_indices(SELECTED_TAB_INDICES, sys_platform)
    nav.refresh_page()

    verify_tabs_reloaded(driver, tabs, time_origins)

    # Step 3: Reload with Ctrl/Cmd + R
    # Reading the time origins of switched tabs, clearing the multi-selection
    time_origins = get_time_origins(driver, page_handles)
    tabs.select_multiple_tabs_by_indices(SELECTED_TAB_INDICES, sys_platform)
    tabs.reload_tab(nav, mod_key=mod_key, extra_key="r")

    verify_tabs_reloaded(driver, tabs, time_origins)

    # Step 4: Reload via the `Reload Tabs` context menu option
    time_origins = get_time_origins(driver, page_handles)
    selected_tabs = tabs.select_multiple_tabs_by_indices(
        SELECTED_TAB_INDICES, sys_platform
    )
    tab_context_menu.context_click(selected_tabs[0])
    tab_context_menu.click_and_hide_menu(RELOAD_SELECTED_TABS)

    verify_tabs_reloaded(driver, tabs, time_origins)
