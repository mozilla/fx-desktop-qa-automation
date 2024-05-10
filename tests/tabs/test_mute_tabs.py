from selenium.webdriver import ActionChains, Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import TabBar


def test_mute_unmute_tab(driver: Firefox, video_url: str):
    # C134719
    tabs = TabBar(driver).open()
    driver.get(video_url)
    play_button = driver.find_element(By.CSS_SELECTOR, ".ytp-play-button")
    play_button.click()
    with driver.context(driver.CONTEXT_CHROME):
        tabs.mute_tab(1)
