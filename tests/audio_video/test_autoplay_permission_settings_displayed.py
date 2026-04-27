import pytest
from selenium.webdriver import Firefox

from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "330151"


def test_block_audio_video_functionality(driver: Firefox):
    """
    C330151: Create test for Block Autoplay permission settings are displayed in about:preferences#privacy
    """
    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")

    # Open privacy and click on the "Settings" button from Autoplay
    about_prefs.open_autoplay_modal()

    # Check that each item of "Default for all websites" menu options are present
    about_prefs.element_exists("autoplay-settings")
    about_prefs.element_exists("allow-audio-video")
    about_prefs.element_exists("block-audio")
    about_prefs.element_exists("block-audio-video")

    # Finally, check that Block Audio option is the default.
    blocked_audio_option = about_prefs.get_element("block-audio")
    assert blocked_audio_option.is_selected()
