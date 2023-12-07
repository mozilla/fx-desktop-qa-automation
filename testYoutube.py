# This test opens a video on Youtube.
# Note: The test will run (and PASS) whether the expected video plays right away or
# if there is an advertisement presented instead.

import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Test(unittest.TestCase):
    def setUp(self):
        # Create a new instance of the browser
        self.options = Options()

        # Firefox Location
        # options.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox-bin"

        # Nightly Location
        self.options.binary_location = "/Applications/Firefox Nightly.app/Contents/MacOS/firefox-bin"

        # self.options.add_argument("-headless")

        self.driver = webdriver.Firefox(options=self.options)

    def test_new_tab(self):

        print(" - TEST: Verify a user can play a Youtube video")
        try:
            # Navigate to a Youtube video
            video_url = "https://www.youtube.com/watch?v=mAia0v3ojzw"
            self.driver.get(video_url)
            WebDriverWait(self.driver, 10).until(EC.url_contains("https://www.youtube.com"))

            # Verify the correct Youtube video page is loaded
            WebDriverWait(self.driver, 10).until(EC.title_contains("Top 10"))
            page_title = self.driver.title
            self.assertEqual(page_title, "Top 10 built-in FireFox features | Compilation | #AskFirefox - YouTube")
            print("Title of the web page is: " + page_title)
            time.sleep(2)

            # Check if the video player is present
            video_player = self.driver.find_element(By.CSS_SELECTOR, ".html5-video-player")
            self.assertTrue(self, video_player.is_displayed())

            # Click on play
            play_button = self.driver.find_element(By.CSS_SELECTOR, ".ytp-play-button")
            play_button.click()

            # Wait for the current time element to be present
            current_time_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.ytp-time-current')))

            # Wait for the video to play for a bit, then get the current play time
            time.sleep(3)
            print(current_time_element.text)
            current_play_time = float(current_time_element.text.split(':')[0]) * 60 + float(
                current_time_element.text.split(':')[1])
            print(f"The running play time should be at least 3 seconds. The value now is {current_play_time} seconds")

            # Assert that the video play time is at least 3 seconds
            self.assertTrue(self, current_play_time >= 3.0)

            # Click the pause the video button
            play_button.click()

        finally:
            # Close the browser after the test is complete
            self.driver.quit()


if __name__ == "__main__":
    unittest.main()
