# Work in progress, but stuck in navigating the FxView page. I'll return to it later.

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

    def test_firefox_view_recently_closed_tab(self):

        print(" - TEST: Verify a user can open a recently closed tab from FxView")
        try:
            # Navigate to an example web page
            example_url = 'https://example.com'
            self.driver.get(example_url)
            WebDriverWait(self.driver, 10).until(EC.url_changes('https://www.example.com/'))

            # Open a new tab
            self.driver.execute_script("window.open('');")

            # Switch to the new tab and open the test page
            self.driver.switch_to.window(self.driver.window_handles[1])
            test_page = "https://wiki.mozilla.org/Test_page"
            self.driver.get(test_page)
            WebDriverWait(self.driver, 10).until(EC.title_contains('Test page - MozillaWiki'))
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

            # Open Recently Closed Tabs section from the sidebar
            # with ((self.driver.context(self.driver.CONTEXT_CONTENT))):
            # Turns out the FxView page is part of the Chrome.  However, finding elements returns empty set.
                # Recently Closed Tabs sidebar element: data-l10n-id: "firefoxview-recently-closed-nav"
                # CSS PATH: html body fxview-category-navigation fxview-category-button.category
                # CSS SELECTOR: fxview-category-button.category:nth-child(4)
                # XPATH:
                # rc_tabs_button = self.driver.find_elements(By.CLASS_NAME,"category")
                # for x in range(len(rc_tabs_button)):
                #    print(rc_tabs_button[x])
                # print(rc_tabs_button)
                # rc_tabs_button.click()
                # WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//fxview-category-button[@data-l10n-id='firefoxview-recently-closed-nav']"))).click()

                # So I'm forced to use keyboard navigation within the page to drive the test steps.
                # And it turns out this is extremely fragile... unusable :(
                pyautogui.PAUSE = 2.0
                pyautogui.moveTo(10,10)
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
