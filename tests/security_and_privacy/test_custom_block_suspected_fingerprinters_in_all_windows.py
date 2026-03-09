import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import PanelUi, TabBar
from modules.page_object import AboutPrefs, GenericPage


@pytest.fixture()
def test_case():
    return "2318652"


@pytest.fixture()
def add_to_prefs_list():
    return [
        (
            "privacy.fingerprintingProtection.overrides",
            "-EfficientCanvasRandomization,+CanvasRandomization",
        ),
    ]


CANVAS_NOISE_URL = "https://arkenfox.github.io/TZP/tests/canvasnoise.html"


def test_custom_block_suspected_fingerprinters_in_all_windows(
    driver: Firefox, panel_ui: PanelUi, tabs: TabBar
):
    """
    C2318652 - Verify canvas randomization protection is active in both normal and private
    windows when "Suspected fingerprinters" is set to "In all windows" in ETP Custom mode.
    Expected: 1st and 2nd reads match each other ([cached]) but not the Control ([matches] absent).
    """
    # Instantiate objects
    about_prefs_privacy = AboutPrefs(driver, category="privacy")
    canvas_page = GenericPage(driver, url=CANVAS_NOISE_URL)

    # Configure ETP Custom: Suspected fingerprinters blocked In all windows
    about_prefs_privacy.open()
    about_prefs_privacy.select_trackers_to_block(
        "suspected-fingerprints-checkbox", "suspected-fingerprints-in-all-windows"
    )

    # Normal window: verify canvas randomization is active
    tabs.open_and_switch_to_new_tab()
    canvas_page.open()
    canvas_page.wait.until(
        lambda d: "[cached]" in d.find_element(By.ID, "readhash2").text
    )
    assert "[matches]" not in canvas_page.find_element(By.ID, "readhash2").text

    # Private window: verify canvas randomization also applies
    panel_ui.open_and_switch_to_new_window("private")
    canvas_page.open()
    canvas_page.wait.until(
        lambda d: "[cached]" in d.find_element(By.ID, "readhash2").text
    )
    assert "[matches]" not in canvas_page.find_element(By.ID, "readhash2").text
