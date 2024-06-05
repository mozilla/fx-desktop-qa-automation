import pytest


@pytest.fixture()
def suite_id():
    return ("2054", "Form Autofill")


# TODO: fix the private browsing so it only triggers the setting for the private browsing test
@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return [
        ("extensions.formautofill.creditCards.reauth.optout", False),
        ("extensions.formautofill.reauth.enabled", False),
        ("browser.privatebrowsing.autostart", True)
    ]
