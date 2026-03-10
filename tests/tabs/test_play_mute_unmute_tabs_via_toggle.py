from time import sleep

import pyautogui
import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import ContextMenu
from modules.browser_object_tabbar import TabBar
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "246981"


@pytest.fixture()
def add_to_prefs_list():
    return [("network.cookie.cookieBehavior", "2")]


@pytest.fixture
def added_selectors() -> dict:
    return {
        "video_selector": {
            "selectorData": "ytd-rich-item-renderer a#video-title-link",
            "strategy": "css",
            "groups": ["doNotCache"],
        }
    }


# This test is unstable in Windows GHA for now
@pytest.mark.audio
@pytest.mark.headed
def test_play_mute_unmute_tabs_via_toggle(
    driver: Firefox, sys_platform: str, added_selectors: dict
):
    """
    C246981 - Verify that play/mute/unmute tabs via toggle audio works
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    DELAY = 2
    POSITION_DELAY = 0.3

    # Open Mozilla's Youtube Page
    playlist_url = "https://www.youtube.com/@Mozilla/videos"
    playlist_page = GenericPage(driver, url=playlist_url)
    playlist_page.open()
    playlist_page.elements |= added_selectors

    # Locate and open 2 latest videos in new tabs
    playlist_page.expect(
        lambda _: len(playlist_page.get_elements("video_selector")) > 2
    )

    # Wait for element before getting all elements
    playlist_page.get_element("video_selector")
    video_links = playlist_page.get_elements("video_selector")

    for i in range(2):
        playlist_page.context_click(video_links[i])
        context_menu.click_and_hide_menu("context-menu-open-link-in-tab")

    # Verify correct number of tabs opened
    tabs.wait_for_num_tabs(3)
    sleep(DELAY)

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

        # Helper function to click the multi-tab audio control button
        def click_multi_tab_audio_button():
            tab = tabs.get_tab(2)
            element_location = tab.location
            element_size = tab.size
            window_position = driver.get_window_position()

            inner_height = driver.execute_script("return window.innerHeight;")
            outer_height = driver.execute_script("return window.outerHeight;")
            chrome_height = outer_height - inner_height

            element_x = (
                window_position["x"]
                + element_location["x"]
                + (element_size["width"] / 2)
            )
            element_y = (
                window_position["y"]
                + element_location["y"]
                + (element_size["height"] / 2)
                + chrome_height
            )
            # Offset to click on the audio control area (left side of tab)
            pyautogui.moveTo(element_x - 75, element_y)
            sleep(POSITION_DELAY)  # Small delay for mouse positioning
            pyautogui.click()
            sleep(DELAY)  # Wait for action to take effect

        # Click Play button
        click_multi_tab_audio_button()

        # Verify all selected tabs are playing
        for i in [2, 3]:
            tabs.expect_tab_sound_status(i, tabs.MEDIA_STATUS.PLAYING)
            tab = tabs.get_tab(i)
            assert tab.get_attribute("soundplaying") is not None, (
                f"Tab {i} should be playing audio"
            )

        # Click Mute button
        click_multi_tab_audio_button()

        # Verify all selected tabs are muted
        for i in [2, 3]:
            tabs.expect_tab_sound_status(i, tabs.MEDIA_STATUS.MUTED)
            tab = tabs.get_tab(i)
            assert tab.get_attribute("muted") is not None, f"Tab {i} should be muted"

        # Click Unmute button
        click_multi_tab_audio_button()

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
