# Work in progress, but stuck in navigating the FxView page. I'll return to it later.
# Turns out, in the FxView page, finding elements returns empty set.
# So I'm forced to use keyboard navigation within the page to drive the test steps,
# which is extremely fragile... unusable :(
# NOTE: New work behind about:config "screenshots.browser.component.enabled"
# may give us access to the elements? Need to figure out how to add that config as tru
# to the profile before this test is run.

import time
import unittest
import pyautogui
import configuration as conf
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class Test(unittest.TestCase):
    def setUp(self):
        # Create a new instance of the browser
        self.options = Options()

        # Firefox/Nightly
        self.options.binary_location = conf.app_location()

        if conf.run_headless() is True:
            self.options.add_argument("--headless")

        self.driver = webdriver.Firefox(options=self.options)

    def test_firefox_view_recently_closed_tab(self):

        print(" - TEST: Verify a user can open a recently closed tab from FxView")
        try:
            # Navigate to an example web page
            example_url = 'https://example.com'
            self.driver.get(example_url)
            WebDriverWait(self.driver, 10).until(ec.url_changes('https://www.example.com/'))

            # Open a new tab
            self.driver.execute_script("window.open('');")

            # Switch to the new tab and open the test page
            self.driver.switch_to.window(self.driver.window_handles[1])
            test_page = "https://wiki.mozilla.org/Test_page"
            self.driver.get(test_page)
            WebDriverWait(self.driver, 10).until(ec.title_contains('Test page - MozillaWiki'))
            print("Title of the page is: " + self.driver.title)

            # Close the current tab containing the test page
            self.driver.close()

            # Open Firefox View
            with self.driver.context(self.driver.CONTEXT_CHROME):
                # Firefox View button element: id:"firefox-view-button"
                fx_view_button = self.driver.find_element(By.ID, "firefox-view-button")
                fx_view_button.click()
                time.sleep(2)
                print("Title of the page is: " + self.driver.title)

                # Open Recently Closed Tabs section from the sidebar.
                pyautogui.PAUSE = 2.0
                pyautogui.moveTo(10, 10)
                pyautogui.press('down')
                pyautogui.press('down')
                pyautogui.press('tab')
                pyautogui.press('enter')
                time.sleep(3)

        finally:
            # Close the browser after the test is complete
            self.driver.quit()


if __name__ == "__main__":
    unittest.main()
