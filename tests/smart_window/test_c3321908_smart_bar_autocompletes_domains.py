"""
C3321908 - Smart bar autocompletes domains
Verify typing into the Smart Bar surfaces autocomplete results, and that
picking the top one navigates to the domain.
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

    # Nothing typed yet, so there is nothing to autocomplete. Asserting this
    # first is what stops the check below passing on a view that was already
    # populated.
    assert bar.get_result_count() == 0, "Smart Bar showed results before any input"

    bar.set_smart_bar_text(DOMAIN)
    bar.expect_results(1)

    # The domain resolves as a navigation rather than a search, which is the
    # behaviour the case is about.
    bar.submit()
    active_smart_window.expect_selected_tab_url_contains(DOMAIN)
