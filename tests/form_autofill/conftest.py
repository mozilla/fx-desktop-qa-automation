import logging
from subprocess import CalledProcessError, check_call

import pytest


@pytest.fixture()
def suite_id():
    return ("2054", "Form Autofill")


@pytest.fixture()
def unlock_keyring(sys_platform: str):
    # TODO: add linux and windows unlocks if relevant
    # TODO: add secrets mgmt and insertion
    if sys_platform != "Darwin":
        return None
    try:
        check_call(["security", "unlock-keychain"])
    except CalledProcessError:
        logging.warning("Failed to unlock keyring: security has errors.")
    except OSError:
        logging.warning("Failed to unlock keyring: security executable not found.")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return [
        ("extensions.formautofill.creditCards.reauth.optout", False),
        ("extensions.formautofill.reauth.enabled", False),
    ]
