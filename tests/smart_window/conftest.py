import pytest

from modules.browser_object_smart_window import SmartWindow


@pytest.fixture()
def suite_id():
    return ("S70279", "Smart Window")


@pytest.fixture()
def prefs_list():
    """
    Smart Window ships disabled by default; every test in this suite needs the
    feature available before the window opens.
    """
    return [("browser.smartwindow.enabled", True)]


@pytest.fixture()
def smart_window(driver):
    """Provide the Smart Window BOM for a window still in the Classic state."""
    return SmartWindow(driver)


@pytest.fixture()
def active_smart_window(driver):
    """
    Provide the Smart Window BOM with the window already in the Smart Window
    state, for tests about behaviour *inside* a Smart Window.

    See SmartWindow.activate_smart_window for why this does not go through the
    product's own (FxA-gated) entry points.
    """
    sw = SmartWindow(driver)
    sw.activate_smart_window()
    return sw
