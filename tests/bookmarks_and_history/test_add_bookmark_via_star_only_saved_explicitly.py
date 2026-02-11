import pytest

from selenium.webdriver import Firefox, ActionChains

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2090394"


BOOKMARK_URL_TO_EDIT = "about:robots"
BOOKMARK_NAME = "ROBOTS"
BOOKMARK_LOCATION = "Bookmarks Toolbar"


def test_add_bookmark_via_star_save_button_explicitly(driver: Firefox):
    """
    C2090394: Verify that adding a Bookmark from the Star button is not saved in real time
    """
    # Instantiate objects
    nav = Navigation(driver)
    page = GenericPage(driver, url="about:robots")
    actions = ActionChains(driver)

    page.open()

    # Start creating a bookmark using the star button and edit the bookmark star dialog fields
    nav.edit_bookmark_via_star_button(
         new_name=BOOKMARK_NAME, location=BOOKMARK_LOCATION, save_bookmark=False
    )

    # Click away from the field inside the dialog
    with nav.driver.context(driver.CONTEXT_CHROME):
        element = nav.panel_ui.get_element("edit-bookmark-panel")
        actions.move_to_element_with_offset(element, 0, -10).click().perform()

    # Confirm the bookmark has not yet been created
    nav.verify_bookmark_does_not_exist_in_bookmarks_toolbar(BOOKMARK_NAME)

    # Finally, save the edited bookmark and verify it exist
    nav.panel_ui.click_on("save-bookmark-button")
    nav.verify_bookmark_exists_in_bookmarks_toolbar(BOOKMARK_NAME)
