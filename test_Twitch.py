# This test searches for Diablo 4 on twitch.

import time
import unittest
import pyautogui
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

        print(" - TEST: Verify a user can search on Twitch")
        try:
            # Navigate to Twitch
            test_url = "https://www.twitch.com"
            self.driver.get(test_url)
            WebDriverWait(self.driver, 10).until(EC.url_contains("https://www.twitch.tv"))

            # Verify the Twitch page is loaded
            WebDriverWait(self.driver, 10).until(EC.title_contains("Twitch"))
            page_title = self.driver.title
            self.assertEqual(page_title, "Twitch")
            print("Title of the web page is: " + page_title)

            # Tab to the search input field and enter "Diablo IV"
            # (had to do this 'cause locating the search field by element wasn't working)
            pyautogui.PAUSE = 1.0
            pyautogui.moveTo(10, 10)
            pyautogui.press('tab', presses=5)
            pyautogui.typewrite("Diablo IV")
            pyautogui.press('enter')

            # Wait for the search results to load
            # CSS SELECTOR: .kEZcIh > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) >
            item_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                '.kEZcIh > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > '
                                                'div:nth-child(1) > strong:nth-child(1) > a:nth-child(1)')))
            item_element_text = item_element.text
            print("Element found by class CSS:", item_element_text)
            self.assertIn("Diablo", item_element_text)

            time.sleep(2)

        finally:
            # Close the browser after the test is complete
            self.driver.quit()


if __name__ == "__main__":
    unittest.main()
