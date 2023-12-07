
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

        self.driver = webdriver.Firefox(options=self.options)

    def test_new_tab(self):

        print(" - TEST: Verify a user can open a page in a new tab")
        try:
            # Navigate to an example web page
            example_url = 'https://example.com'
            self.driver.get(example_url)
            WebDriverWait(self.driver, 10).until(EC.url_changes('https://www.example.com/'))

            # Open another page in a new tab
            with self.driver.context(self.driver.CONTEXT_CHROME):
                newtab_button = self.driver.find_element(By.ID, "tabs-newtab-button")
                newtab_button.click()
                time.sleep(1)
                self.driver.find_element(By.ID, 'urlbar-input').send_keys(
                    "https://www.w3.org/People/mimasa/test/" + Keys.ENTER)
                time.sleep(1)

            # Verify the new page is opened
            with self.driver.context(self.driver.CONTEXT_CONTENT):
                self.driver.switch_to.window(self.driver.window_handles[1])
                WebDriverWait(self.driver, 10).until(EC.title_contains('Test'))
                page_title = self.driver.title
                self.assertEqual(page_title, "Test page")
                print("Title of the web page is: " + page_title)
                time.sleep(3)

        finally:
            # Close the browser after the test is complete
            self.driver.quit()



if __name__ == "__main__":
    unittest.main()
