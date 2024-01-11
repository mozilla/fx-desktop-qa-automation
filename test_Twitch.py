# This test searches for Diablo 4 on twitch.

import time
import unittest
import configuration as conf
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class Test(unittest.TestCase):
    def setUp(self):
        # Create a new instance of the browser
        self.options = Options()

        # Firefox/Nightly location
        self.options.binary_location = conf.app_location()

        if conf.run_headless() is True:
            self.options.add_argument("--headless")

        self.driver = webdriver.Firefox(options=self.options)

    def test_new_tab(self):

        print(" - TEST: Verify a user can search on Twitch")
        try:
            # Navigate to Twitch
            test_url = "https://www.twitch.com"
            self.driver.get(test_url)
            WebDriverWait(self.driver, 10).until(ec.url_contains("https://www.twitch.tv"))

            # Verify the Twitch page is loaded
            WebDriverWait(self.driver, 10).until(ec.title_contains("Twitch"))
            page_title = self.driver.title
            self.assertEqual(page_title, "Twitch")
            print("Title of the web page is: " + page_title)

            # Find the search input field and enter "Diablo IV"
            search_input = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-label="Search Input"]')))
            search_input.send_keys("Diablo IV")
            search_input.send_keys(Keys.RETURN)

            # Wait for the search results to load
            item_element = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR,
                                                '.kEZcIh > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > '
                                                'div:nth-child(1) > strong:nth-child(1) > a:nth-child(1)')))
            item_element_text = item_element.text
            print("Element found by CSS:", item_element_text)
            self.assertIn("Diablo", item_element_text)

            time.sleep(2)

        finally:
            # Close the browser after the test is complete
            self.driver.quit()


if __name__ == "__main__":
    unittest.main()
