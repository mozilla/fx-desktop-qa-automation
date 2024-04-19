# This test opens a video on Youtube.
# Note: The test will run (and PASS) whether the expected video plays right away or
# if there is an advertisement presented instead.

import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


@pytest.fixture()
def test_url():
    return "https://www.youtube.com/watch?v=mAia0v3ojzw"


@pytest.mark.incident
def test_youtube_search(driver, test_url):
    print(" - TEST: Verify a user can play a Youtube video")

    # Navigate to a Youtube video
    driver.get(test_url)
    WebDriverWait(driver, 10).until(EC.url_contains("https://www.youtube.com"))

    # Verify the correct YouTube video page is loaded
    WebDriverWait(driver, 10).until(EC.title_contains("Top 10"))
    page_title = driver.title
    assert (
        page_title
        == "Top 10 built-in Firefox features | Compilation | #AskFirefox - YouTube"
    )
    print("Title of the web page is: " + page_title)
    time.sleep(2)

    # Check if the video player is present
    video_player = driver.find_element(By.CSS_SELECTOR, ".html5-video-player")
    assert video_player.is_displayed()

    # Click on play
    play_button = driver.find_element(By.CSS_SELECTOR, ".ytp-play-button")
    play_button.click()

    # Wait for the current time element to be present
    current_time_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".ytp-time-current"))
    )

    # Wait for the video to play for a bit, then get the current play time
    time.sleep(3)
    print(current_time_element.text)
    current_play_time = float(current_time_element.text.split(":")[0]) * 60 + float(
        current_time_element.text.split(":")[1]
    )
    print(
        f"The running play time should be at least 2 seconds. The value now is {current_play_time} seconds"
    )

    # Assert that the video play time is at least 2 seconds
    assert current_play_time >= 2.0

    # Click the pause the video button
    play_button.click()
