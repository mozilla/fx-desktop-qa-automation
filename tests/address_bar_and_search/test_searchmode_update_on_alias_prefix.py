import pytest
from selenium.webdriver import Firefox, Keys

from modules.browser_object_navigation import Navigation


ENGINE_KEYWORD = "@bing"
TEXT = "QA"
ENGINE = "Bing"


@pytest.fixture()
def test_case():
    return "3028841"


def test_searchmode_update_on_alias_prefix(driver: Firefox):
    """
    C3028841 - Search mode is updated after typing a keyword/alias at the beginning of a non-empty search string
    """

    # Instantiate objects
    nav = Navigation(driver)

    # TODO: Go to about:preferences#search and set a keyword for bing, for example: bang

    # Open a new tab, focus the urlbar and enter any string
    nav.type_in_awesome_bar(TEXT)

    # Start pressing LEFT KEY on the keyboard so the text insertion cursor is at the beginning
    for _ in range(2):
        nav.perform_key_combo_chrome(Keys.LEFT)

    # Type @bing and press SPACE
    nav.type_in_awesome_bar(ENGINE_KEYWORD, reset=False)
    nav.perform_key_combo_chrome(Keys.SPACE)

    # Search shortcut should be identified and translated to search mode for bing with the original text
    # remaining as search query
    nav.verify_engine_returned(ENGINE)
    nav.verify_plain_text_in_input_awesome_bar(TEXT)
