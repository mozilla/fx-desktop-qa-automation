import pytest

from modules.page_object import AboutAddons, AboutPrefs, AmoLanguages


@pytest.fixture()
def suite_id():
    return ("S22801", "Language Packs")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = [
        ("intl.multilingual.downloadEnabled", True),
        ("intl.multilingual.enabled", True),
        ("intl.multilingual.liveReload", True),
    ]
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []


@pytest.fixture()
def amo_languages(driver):
    return AmoLanguages(driver)


@pytest.fixture()
def about_addons(driver):
    return AboutAddons(driver)


@pytest.fixture()
def about_prefs(driver):
    return AboutPrefs(driver, category="general")
