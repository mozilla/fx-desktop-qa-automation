import pytest


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return [
        ("extensions.formautofill.creditCards.reauth.optout", False),
        ("extensions.formautofill.reauth.enabled", False),
        ("browser.aboutConfig.showWarning", False),
        ("browser.search.region", "US"),
    ]
