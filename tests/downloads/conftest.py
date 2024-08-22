import os

import pytest


@pytest.fixture()
def suite_id():
    return ("S29219", "Downloads")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
