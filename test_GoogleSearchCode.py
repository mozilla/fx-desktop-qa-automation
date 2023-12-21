import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

    def test_google_search_code(self):

        print(" - TEST: Verify Firefox search code for Google SERP")
        try:
            # Enter Search term in URL bar
            with self.driver.context(self.driver.CONTEXT_CHROME):
                self.driver.find_element(By.ID, 'urlbar-input').send_keys("soccer" + Keys.RETURN)
                time.sleep(3)

            # Check that the search url contains the appropriate search code
            with self.driver.context(self.driver.CONTEXT_CONTENT):
                expected_code = "firefox-b-d&q=soccer"
                WebDriverWait(self.driver, 10).until(EC.title_contains('Google Search'))
                print("The web page is: " + self.driver.title)
                search_url = self.driver.current_url
                print("The current url is: " + str(search_url))
                self.assertRegex(search_url, expected_code)
                time.sleep(3)

        finally:
            # Close the browser after the test is complete
            self.driver.quit()


if __name__ == "__main__":
    unittest.main()
