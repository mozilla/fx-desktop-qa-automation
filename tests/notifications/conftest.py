import pytest


@pytest.fixture()
def suite_id():
    return ("1907", "Notifications, Push Notifications and Alerts")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
