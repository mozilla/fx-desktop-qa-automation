import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import AboutPrefs
from modules.util import Utilities

# Browser regions in which the Credit cards can be saved in
countries = ["CA", "US"]


@pytest.mark.parametrize("country_code", countries)
def test_create_new_cc_profile(driver: Firefox, country_code: str):
    """
    C122389, tests you can create and save a new Credit Card profile
    """
    # Instantiate objects
    Navigation(driver).open()
    about_prefs = AboutPrefs(driver, category="privacy").open()
    util = Utilities()
    new_credit_card_data = util.fake_credit_card_data()

    # Go to Preferences(Options)/ Privacy and Security / Form Autofill Saved CC
    about_prefs.get_element("saved-payment-methods-button").click()

    # Click on Add
    with driver.context(driver.CONTEXT_CHROME):
        about_prefs.get_element("add_card_button").click()


# Note that a billing address needs to be added in Saved Addresses in order to create a new Credit Card entry
# Fill in fields and click Save
# Click on the saved CC
