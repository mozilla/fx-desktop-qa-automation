import pytest
from selenium.webdriver import Firefox


@pytest.fixture()
def test_case():
    return "2090393"


def test_add_bookmark_via_toolbar_not_saving_realtime(driver: Firefox):
    """
    C2090393 - Verify that adding a Bookmark from the Bookmarks toolbar is not saved in real time
    """

    # Instantiate objects

    # Right-click the Bookmarks Toolbar and select Add Bookmark

    # The New Bookmark is not displayed on the Bookmarks Toolbar

    # Add any text to each field

    # The Bookmark is still not created after clicking outside of the Edit fields

    # Click the Save button

    # The Bookmark is corectly created
