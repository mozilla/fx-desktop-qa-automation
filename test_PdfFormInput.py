import time
import unittest
import os
import platform
import keyboard
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

        # Firefox/Nightly location
        self.options.binary_location = conf.app_location()

        if conf.run_headless() is True:
            self.options.add_argument("--headless")

        self.driver = webdriver.Firefox(options=self.options)

    def test_pdf_form_fill(self):

        # From TestRail: https://testrail.stage.mozaws.net/index.php?/cases/view/1017484
        print(" - TEST: Verify PDF form input")
        try:
            # Navigate to the test form
            test_url = 'http://foersom.com/net/HowTo/data/OoPdfFormExample.pdf'
            self.driver.get(test_url)
            WebDriverWait(self.driver, 10).until(ec.url_changes('foersom.com/net/HowTo/data/OoPdfFormExample.pdf'))

            # Enter full name in the PDF form fields
            # Given name text box element: id=pdfjs_internal_id_5R value="" name="Given Name Text Box"
            given_name_field = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((By.ID, "pdfjs_internal_id_5R")))
            given_name_field.send_keys("Mary")

            # Family name text box element: id=pdfjs_internal_id_7R value="" name="Family Name Text Box"
            family_name_field = self.driver.find_element(By.ID, "pdfjs_internal_id_7R")
            family_name_field.send_keys("Smithsonian")

            # Save the PDF to Downloads
            download_button = self.driver.find_element(By.ID, "download")
            download_button.click()

            # Wait for the system Save dialog
            time.sleep(2)
            keyboard.send('enter')

            # Wait for the download to complete
            time.sleep(3)

            # Open a new tab after making the first tab blank
            self.driver.get('about:blank')
            print('The title of the tab should be blank !' + self.driver.title + '! <- Nothing between those')
            self.driver.execute_script("window.open('');")

            # Determine system user and set paths per platform
            user = os.environ.get('USER')
            this_platform = platform.system()
            saved_pdf_location = ""
            if this_platform == 'Windows':
                saved_pdf_location = "C:\\Users\\" + user + "\\Downloads\\OoPdfFormExample.pdf"
            elif this_platform == 'Darwin':
                saved_pdf_location = "/Users/" + user + "/Downloads/OoPdfFormExample.pdf"
            elif this_platform == 'Linux':
                saved_pdf_location = "/home/" + user + "/Downloads/OoPdfFormExample.pdf"

            saved_pdf_url = "file://" + saved_pdf_location

            # Switch to the new tab and open the saved PDF
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.get(saved_pdf_url)
            WebDriverWait(self.driver, 10).until(ec.title_contains('PDF Form Example'))
            print("Title of the loaded file is: " + self.driver.title)

            # Verify the values in the form fields are correctly filled in
            given_name_saved = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((By.ID, "pdfjs_internal_id_5R")))
            given_value = given_name_saved.get_attribute("value")
            print("The value of the Given name is '" + given_value + "' <- should be 'Mary'")
            self.assertEqual(given_value, "Mary")
            family_name_saved = self.driver.find_element(By.ID, "pdfjs_internal_id_7R")
            family_value = family_name_saved.get_attribute("value")
            print("The value of the Family name is '" + family_value + "' <- should be 'Smithsonian'")
            self.assertEqual(family_value, "Smithsonian")

            # Close the current tab containing the PDF
            self.driver.close()

            # remove the downloaded PDF from the system
            try:
                os.remove(saved_pdf_location)
                print(saved_pdf_location + " has been deleted.")
            except OSError as error:
                print("There was an error.")
                print(error)

        finally:
            # Close the browser after the test is complete
            self.driver.quit()


if __name__ == "__main__":
    unittest.main()
