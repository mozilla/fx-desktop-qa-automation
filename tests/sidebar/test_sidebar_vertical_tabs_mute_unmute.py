import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, TabBar

VIDEO_URL = "https://www.w3schools.com/html/mov_bbb.mp4"


@pytest.fixture()
def test_case():
    return "2652383"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.tabs.delayHidingAudioPlayingIconMS", "200"),
    ]


@pytest.mark.audio
def test_sidebar_vertical_tabs_mute_unmute(driver: Firefox):
    """
    C2652383 - Verify that vertical tabs in the sidebar can be muted and unmuted via context menu option and keyboard
    shortcut, and that the correct sound status is displayed in the tab.
    """

    # Instantiate objects
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)

    # Enable vertical tabs
    nav.toggle_vertical_tabs()

    # Open a media tab and wait for audio to start playing
    driver.get(VIDEO_URL)
    tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.PLAYING)

    # Mute the tab via context menu and verify it is muted
    tabs.context_click(tabs.get_tab(1))
    context_menu.click_and_hide_menu("context-menu-toggle-mute-tab")
    tabs.hide_popup("tabContextMenu")
    tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.MUTED)

    # Unmute the tab via context menu and verify it is playing again
    tabs.context_click(tabs.get_tab(1))
    context_menu.click_and_hide_menu("context-menu-toggle-mute-tab")
    tabs.hide_popup("tabContextMenu")
    tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.PLAYING)

    # Mute via CTRL+M and verify
    tabs.toggle_mute_shortcut()
    tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.MUTED)

    # Unmute via CTRL+M and verify
    tabs.toggle_mute_shortcut()
    tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.PLAYING)
