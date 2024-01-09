# This test searches for a soccer ball on Amazon.
#  It breaks after a while due to bot identification by Amazon

import time
import unittest
import configuration as conf
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
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

        # Remove navigator.webdriver Flag using JavaScript to avoid bot detection by Amazon
        # NOTE: This worked for a while, then it intermittently stops working and Amazon Captcha got us again.
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def test_amazon_search(self):

        print(" - TEST: Verify a user can search on Amazon")
        try:
            # Navigate to Amazon
            test_url = "https://www.amazon.com"
            self.driver.get(test_url)
            WebDriverWait(self.driver, 10).until(ec.url_contains("https://www.amazon.com"))

            # Verify the Amazon page is loaded
            WebDriverWait(self.driver, 10).until(ec.title_contains("Amazon.com"))
            page_title = self.driver.title
            self.assertEqual(page_title, "Amazon.com. Spend less. Smile more.")
            print("Title of the web page is: " + page_title)

            # Find the search input field and enter "soccer ball"
            search_input = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((By.ID, "twotabsearchtextbox"))
            )
            time.sleep(2)
            search_input.send_keys("soccer ball", Keys.RETURN)

            # Wait for the search results to load
            item_element = (WebDriverWait(self.driver, 10).until
                            (ec.presence_of_element_located
                             ((By.XPATH, "//html/body/div[1]/div[1]/span[2]/div/h1/div/div[1]/div/div/span[3]"))))
            item_element_text = item_element.text
            print("Element found by class name:", item_element_text)
            self.assertIn("soccer ball", item_element_text)

            time.sleep(2)

        finally:
            # Close the browser after the test is complete
            self.driver.quit()


if __name__ == "__main__":
    unittest.main()
