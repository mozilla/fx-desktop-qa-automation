import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object_panel_ui import PanelUi
from modules.browser_object_tabbar import TabBar
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "2318653"


@pytest.fixture()
def add_to_prefs_list():
    return [
        (
            "privacy.fingerprintingProtection.overrides",
            "-EfficientCanvasRandomization,+CanvasRandomization",
        ),
    ]


CANVAS_NOISE_URL = "https://arkenfox.github.io/TZP/tests/canvasnoise.html"


def test_custom_block_suspected_fingerprinters_only_in_private_windows(driver: Firefox):
    """
    C2318653 - Verify canvas randomization protection is active only in private windows
    when "Suspected fingerprinters" is set to "Only in private windows" in ETP Custom mode.
    Expected normal window: reads match the Control ([matches] present).
    Expected private window: 1st and 2nd reads match each other ([cached]) but not the Control ([matches] absent).
    """
    # Instantiate objects
    panel = PanelUi(driver)
    about_prefs_privacy = AboutPrefs(driver, category="privacy")
    tabs = TabBar(driver)
    canvas_page = GenericPage(driver, url=CANVAS_NOISE_URL)

    # Configure ETP Custom: Suspected fingerprinters blocked In all windows
    about_prefs_privacy.open()
    about_prefs_privacy.select_trackers_to_block(
        "suspected-fingerprints-checkbox",
        "suspected-fingerprints-only-in-private-windows",
    )

    # Normal window: verify canvas randomization is NOT active
    tabs.open_and_switch_to_new_tab()
    canvas_page.open()
    canvas_page.wait.until(
        lambda d: "[matches]" in d.find_element(By.ID, "readhash2").text
    )
    assert "[matches]" in canvas_page.find_element(By.ID, "readhash2").text

    # Private window: verify canvas randomization is active
    panel.open_and_switch_to_new_window("private")
    canvas_page.open()
    canvas_page.wait.until(
        lambda d: "[cached]" in d.find_element(By.ID, "readhash2").text
    )
    assert "[matches]" not in canvas_page.find_element(By.ID, "readhash2").text
