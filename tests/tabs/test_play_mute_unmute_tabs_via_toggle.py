from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from modules.browser_object import ContextMenu
from modules.browser_object_tabbar import TabBar
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "246981"


@pytest.fixture()
def add_to_prefs_list():
    return [("network.cookie.cookieBehavior", "2")]


# This test is unstable in Windows GHA for now
@pytest.mark.audio
@pytest.mark.headed
def test_play_mute_unmute_tabs_via_toggle(driver: Firefox, sys_platform: str):
    """
    C246981 - Verify that play/mute/unmute tabs via toggle audio works
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    wait = WebDriverWait(driver, 10)

    playlist_url = "https://www.youtube.com/@msrachel"
    playlist_page = GenericPage(driver, url=playlist_url)
    playlist_page.open()

    # Locate and open 2 latest videos in new tabs
    video_selector = ".ytThumbnailViewModelHost"
    video_links = wait.until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, video_selector))
    )

    for i in range(2):
        playlist_page.context_click(video_links[i])
        context_menu.click_and_hide_menu("context-menu-open-link-in-tab")

    # Verify correct number of tabs opened
    tabs.wait_for_num_tabs(3)

    # Select all tabs via Control/Command click while staying on first tab
    modifier_key = Keys.COMMAND if sys_platform == "Darwin" else Keys.CONTROL

    with driver.context(driver.CONTEXT_CHROME):
        actions = tabs.actions

        # Hold modifier and select the video tabs
        actions.key_down(modifier_key)
        for i in range(2, 4):  # Select tabs 2 and 3
            tab_to_select = tabs.get_tab(i)
            actions.click(tab_to_select)
        actions.key_up(modifier_key).perform()

        # Verify tabs are selected (multiselected attribute)
        for i in range(2, 4):
            tab = tabs.get_tab(i)
            assert tab.get_attribute("multiselected") == "true", (
                f"Tab {i} should be multiselected"
            )

        # Click Play button
        tabs.click_multi_tab_audio_button()

        # Verify all selected tabs are playing
        for i in [2, 3]:
            tabs.expect_tab_sound_status(i, tabs.MEDIA_STATUS.PLAYING)
            tab = tabs.get_tab(i)
            assert tab.get_attribute("soundplaying") is not None, (
                f"Tab {i} should be playing audio"
            )

        # Click Mute button
        tabs.click_multi_tab_audio_button()

        # Verify all selected tabs are muted
        for i in [2, 3]:
            tabs.expect_tab_sound_status(i, tabs.MEDIA_STATUS.MUTED)
            tab = tabs.get_tab(i)
            assert tab.get_attribute("muted") is not None, f"Tab {i} should be muted"

        # Click Unmute button
        tabs.click_multi_tab_audio_button()

        # Verify all selected tabs are unmuted and playing again
        for i in [2, 3]:
            tabs.expect_tab_sound_status(i, tabs.MEDIA_STATUS.PLAYING)
            tab = tabs.get_tab(i)
            assert tab.get_attribute("soundplaying") is not None, (
                f"Tab {i} should be playing audio after unmute"
            )
            assert tab.get_attribute("muted") is None, (
                f"Tab {i} should not be muted after unmute"
            )
