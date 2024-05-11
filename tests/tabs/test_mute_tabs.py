from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

from modules.browser_object import TabBar


def test_mute_unmute_tab(screenshot, driver: Firefox, video_url: str):
    # C134719
    driver.get("about:support")
    ac = ActionChains(driver)
    ac.move_to_element_with_offset(driver.find_element(By.ID, "useragent-box"))
    screenshot("about-support")
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
