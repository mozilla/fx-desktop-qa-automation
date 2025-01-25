import logging
import platform
import subprocess

import pytest


@pytest.fixture()
def suite_id():
    return ("2054", "Form Autofill")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return [
        ("extensions.formautofill.creditCards.reauth.optout", False),
        ("extensions.formautofill.reauth.enabled", False),
    ]


@pytest.fixture()
def kill_gnome_keyring():
    """Kill the gnome keyring daemon long enough to finish a test"""
    if platform.system != "Linux":
        return False
    try:
        subprocess.Popen[".", "./keyring-unlock.sh"]
    except subprocess.CalledProcessError:
        logging.warning("Tried to kill gnome-keyring-daemon, but failed.")
