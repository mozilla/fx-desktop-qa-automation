import json
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.classes.credit_card import CreditCardBase
from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "3056980"


def test_create_new_cc_profile(
    driver: Firefox,
    region: str,
    about_prefs_payments: AboutPrefs,
    populate_saved_payments: CreditCardBase,
):
    """
    C3056980 - Tests you can create and save a new Credit Card profile
    """
    # get sample data
    credit_card_sample_data = populate_saved_payments

    # sleep(100)

    cc_info_json = about_prefs_payments.get_data_from_saved_payment()

    # Compare input CC data with saved CC data
    about_prefs_payments.verify_cc_json(cc_info_json, credit_card_sample_data)
