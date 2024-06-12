import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import TabBar


@pytest.mark.audio
def test_mute_unmute_tab(screenshot, driver: Firefox, video_url: str):
    # C134719
    tabs = TabBar(driver).open()
    driver.get(video_url)
    play_button = driver.find_element(By.CSS_SELECTOR, ".ytp-play-button")
    play_button.click()
    with driver.context(driver.CONTEXT_CHROME):
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.PLAYING)
        tabs.click_tab_mute_button(1)
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.MUTED)
        tabs.click_tab_mute_button(1)
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.PLAYING)
