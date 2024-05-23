import pytest
from selenium.webdriver import Firefox

# from selenium.webdriver.firefox.options import Options
from modules.browser_object import Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs, AddressFill
from modules.util import Utilities

countries = ["CA", "US"]

import logging

# Setup logging
logging.basicConfig(
    filename="test_results.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


# @pytest.mark.parametrize("country_code", countries)
# def test_enable_disable_autofill(driver: Firefox, country_code: str):
#     """
#     C122347, tests that after filling autofill and disabling it in settings that
#     the autofill popups do not appear.
#     """
#     # instantiate objects
#     Navigation(driver).open()
#     af = AddressFill(driver).open()
#     afp = AutofillPopup(driver)
#     util = Utilities()

#     # create fake data, fill it in and press submit and save on the doorhanger
#     autofill_sample_data = util.fake_autofill_data(country_code)
#     af.save_information_basic(autofill_sample_data)
#     afp.press_doorhanger_save()
#     about_prefs = AboutPrefs(driver, category="privacy").open()
#     about_prefs.get_element("save-and-fill-addresses").click()

#     # creating new objects to prevent stale webelements
#     new_af = AddressFill(driver).open()
#     new_af = AddressFill(driver).open()
#     new_afp = AutofillPopup(driver)

#     # verifying the popup panel does not appear
#     new_af.double_click("form-field", "name")
#     new_afp.verify_no_popup_panel()


def test_telephone_attribute_autofill(driver: Firefox):
    """
    C122361
    """
    # instantiate objects
    Navigation(driver).open()
    af = AddressFill(driver).open()
    afp = AutofillPopup(driver)
    util = Utilities()

    # create fake data, fill it in and press submit and save on the doorhanger
    autofill_sample_data = util.fake_autofill_data("CA")
    af.save_information_basic(autofill_sample_data)
    afp.press_doorhanger_save()

    # double click telephone attribute
    af.double_click("form-field", "tel")
    first_item = afp.get_nth_element("1")

    afp.hover_over_element(first_item)

    actual_value = afp.get_primary_value(first_item)
    # print(actual_value)
    # print(autofill_sample_data.telephone)


# def run_tests():
#     driver = get_headless_driver()
#     try:
#         for i in range(100):
#             for country in countries:
#                 test_telephone_attribute_autofill(driver, country)
#     finally:
#         driver.quit()

# def get_headless_driver():
#     options = Options()
#     options.headless = True
#     driver = Firefox(options=options)
#     return driver

# # Call the function to execute the tests
# run_tests()
