# This test searches for a soccer ball on Amazon.
#  It breaks after a while due to bot identification by Amazon

import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
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
        # attempt to spoof a real browser user to avoid robot detection (doesn't work)
        # self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)
        #       AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

        self.driver = webdriver.Firefox(options=self.options)

        # Remove navigator.webdriver Flag using JavaScript to avoid bot detection by Amazon
        # NOTE: This worked for a while, then I stopped working and Amazon Capta'd again.
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def test_amazon_search(self):

        print(" - TEST: Verify a user can search on Amazon")
        try:
            # Navigate to Amazon
            test_url = "https://www.amazon.com"
            self.driver.get(test_url)
            WebDriverWait(self.driver, 10).until(EC.url_contains("https://www.amazon.com"))

            # Verify the Amazon page is loaded
            WebDriverWait(self.driver, 10).until(EC.title_contains("Amazon.com"))
            page_title = self.driver.title
            self.assertEqual(page_title, "Amazon.com. Spend less. Smile more.")
            print("Title of the web page is: " + page_title)

            # Find the search input field and enter "soccer ball"
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
            )
            time.sleep(2)
            search_input.send_keys("soccer ball", Keys.RETURN)

            # Wait for the search results to load
            # XPATH: html/body/div[1]/div[1]/div[1]/div[1]/div/span[1]/div[1]/div[3]/div/div/div/div/span/div/div/div[3]/div[1]/h2/a/span
            # EC.presence_of_element_located((By.XPATH, "//div[1]/div[1]/div[1]/div[1]/div/span[1]/div[1]/div[3]/div/div/div/div/span/div/div/div[3]/div[1]/h2/a/span")))
            item_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                            "span[data-component-type='s-search-results'] div.s-card-container span.a-text-normal")))
            item_element_text = item_element.text
            print("Element found by class name:", item_element_text)
            self.assertIn("Soccer", item_element_text)

            time.sleep(2)

        finally:
            # Close the browser after the test is complete
            self.driver.quit()


if __name__ == "__main__":
    unittest.main()
