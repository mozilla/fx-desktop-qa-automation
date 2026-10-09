"""
C3321908 - Smart bar autocompletes domains
Verify typing into the Smart Bar surfaces autocomplete results, and that the
domain resolves as a navigation.
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import SmartBar, SmartWindow

DOMAIN = "example.com"


@pytest.fixture()
def test_case():
    return "3321908"


def test_smart_bar_autocompletes_domains(
    driver: Firefox, active_smart_window: SmartWindow
):
    """
    C3321908 - Smart bar autocompletes domains
    """
    bar = SmartBar(driver)
    bar.open_smart_bar()

    bar.expect_no_results()
    bar.set_smart_bar_text(DOMAIN)
    bar.expect_results(1)

    bar.submit()
    active_smart_window.expect_selected_tab_url_contains(DOMAIN)
