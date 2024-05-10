from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import TabBar


def test_mute_unmute_tab(driver: Firefox, screenshot, video_url: str):
    # C134719
    tabs = TabBar(driver).open()
    driver.get(video_url)
    play_button = driver.find_element(By.CSS_SELECTOR, ".ytp-play-button")
    play_button.click()
    with driver.context(driver.CONTEXT_CHROME):
        tabs.click_tab_mute_button(1)
        tabs.actions.move_to_element(tabs.get_tab(1))
        screenshot("should_be_muted")
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.MUTED)
        tabs.click_tab_mute_button(1)
        tabs.expect_tab_sound_status(1, tabs.MEDIA_STATUS.PLAYING)
