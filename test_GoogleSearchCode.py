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

    def test_google_search_code(self):

        print(" - TEST: Verify Firefox search code for Google SERP")
        try:
            # Enter Search term in URL bar
            with self.driver.context(self.driver.CONTEXT_CHROME):
                self.driver.find_element(By.ID, 'urlbar-input').send_keys("soccer" + Keys.RETURN)

            # Check that the search url contains the appropriate search code
            with self.driver.context(self.driver.CONTEXT_CONTENT):
                fx_code = "firefox-b-d"
                WebDriverWait(self.driver, 10).until(ec.title_contains('Google Search'))
                search_url = self.driver.current_url
                print("The current url is: " + str(search_url))
                assert ec.url_contains(fx_code)

        finally:
            # Close the browser after the test is complete
            self.driver.quit()


if __name__ == "__main__":
    unittest.main()
