import random
from time import sleep
from typing import List, Optional, Tuple

from pypom import Region
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from modules.components.dropdown import Dropdown
from modules.page_base import BasePage
from modules.util import BrowserActions, PomUtils


class PanelUi(BasePage):
    """Browser Object Model for nav panel UI menu (hamburger menu, application menu)"""

    URL_TEMPLATE = "about:blank"
    ENABLE_ADD_TAG = (
        """PlacesUtils.tagging.tagURI(makeURI("https://www.github.com"), ["tag1"]);"""
    )

    class Menu(Region):
        """
        PyPOM Region factory for the PanelUi Dropdown menu
        """

        def __init__(self, page, **kwargs):
            super().__init__(page, **kwargs)
            self.utils = PomUtils(self.driver)

        @property
        def loaded(self):
            targeted = [
                el
                for el in self.page.elements.values()
                if "requiredForPage" in el["groups"] and "menuItem" in el["groups"]
            ]
            return all([EC.presence_of_element_located(el) for el in targeted])

    @BasePage.context_chrome
    def open_panel_menu(self) -> BasePage:
        """
        Opens the PanelUi menu.
        """
        panel_root = self.get_element("panel-ui-button")
        panel_root.click()
        self.menu = self.Menu(self, root=panel_root)
        sleep(2)  # Bug 1974080
        return self

    def navigate_to_about_addons(self):
        """
        On the hamburger menu > More Tools > Customize Toolbar > Manage Themes
        """
        self.click_on("more-tools")
        self.click_on("customize-toolbar")
        self.click_on("manage-themes")

    def navigate_to_customize_toolbar(self):
        """
        On the hamburger menu > More Tools > Customize Toolbar
        """
        self.click_on("more-tools")
        self.click_on("customize-toolbar")

    def click_sync_sign_in_button(self) -> BasePage:
        """
        Click FxA sync button.
        """
        self.open_panel_menu()
        self.click_on("fxa-sign-in")
        return self

    def open_account_toolbar(self):
        """
        Open the FxA account toolbar.
        """
        self.click_on("sync-user-button")
        return self

    def click_finish_sign_in_button(self):
        """
        Click FxA finish sign in button.
        """
        self.open_account_toolbar()
        self.click_on("fxa-finish-sign-in")
        return self

    def log_out_fxa(self) -> BasePage:
        """
        Click FxA signout button.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.click_sync_sign_in_button()
            self.get_element("fxa-sign-out-button").click()
        return self

    def manage_fxa_account(self) -> BasePage:
        """
        Open the FxA management flow.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.click_sync_sign_in_button()
            self.get_element("fxa-manage-account-button").click()
        return self

    @BasePage.context_chrome
    def manage_fxa_finish_sign_in(self):
        """
        Open the FxA management flow to finish sign in.
        """
        self.open_account_toolbar()
        self.click_on("fxa-manage-account-button")
        return self

    def confirm_sync_in_progress(self) -> BasePage:
        """
        Check that FxA Sync Label is set to "Syncing…"
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.click_sync_sign_in_button()
            try:
                self.instawait.until(
                    EC.text_to_be_present_in_element(
                        self.get_selector("fxa-sync-label"), "Sync"
                    )
                )
            except (NoSuchElementException, TimeoutException):
                self.get_element("panel-ui-button").click()
                self.click_sync_sign_in_button()
            self.custom_wait(timeout=30, poll_frequency=0.5).until(
                EC.text_to_be_present_in_element(
                    self.get_selector("fxa-sync-label"), "Syncing"
                )
            )
        return self

    def start_sync(self) -> BasePage:
        """
        Start FxA sync
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.click_sync_sign_in_button()
            self.element_has_text("fxa-sync-label", "Sync now")
            self.get_element("fxa-sync-label").click()
        return self

    def open_private_window(self) -> BasePage:
        """
        Opens a new window in private browsing mode using the panel
        """
        self.open_panel_menu()
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("panel-ui-new-private-window").click()
        return self

    @BasePage.context_chrome
    def redirect_to_about_logins_page(self) -> BasePage:
        """
        Opens the about:logins page by clicking the Password option in Hamburger Menu"
        """
        self.open_panel_menu()
        self.get_element("password-button").click()
        return self

    @BasePage.context_chrome
    def reopen_recently_closed_tabs(self) -> BasePage:
        """Navigate to Hamburger > History > Recently Closed Tabs subview."""
        self.open_panel_menu()
        self.click_on("panel-ui-history")
        self.click_on("panel-ui-history-recently-closed")
        sleep(2)
        self.click_on("panel-ui-history-recently-closed-reopen-tabs")
        return self

    # History

    @BasePage.context_chrome
    def open_history_menu(self) -> BasePage:
        """
        Opens the History menu
        """
        self.open_panel_menu()
        self.click_on("panel-ui-history")
        return self

    @BasePage.context_chrome
    def open_clear_history_dialog(self) -> BasePage:
        """
        Opens the clear history dialog and switches to iframe context, assuming the history panel is opened
        """
        self.click_on("clear-recent-history")

        # Switch to iframe
        self.element_visible("iframe")
        iframe = self.get_element("iframe")
        BrowserActions(self.driver).switch_to_iframe_context(iframe)
        return self

    @BasePage.context_content
    def select_history_time_range_option(self, option: str) -> BasePage:
        """
        Selects time range option (assumes already in iframe context)
        """
        dropdown_root = self.get_element("clear-history-dropdown")
        dropdown = Dropdown(page=self, root=dropdown_root, require_shadow=False)
        dropdown.select_option(option)
        return self

    def get_all_history(self) -> List[WebElement]:
        """
        Gets all history items
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            history_items = self.get_elements("bookmark-item")
            return history_items

    @BasePage.context_chrome
    def verify_most_recent_history_item(self, expected_value: str) -> BasePage:
        """
        Verify that the specified value is the most recent item in the history menu.
        Argument:
            Expected_value (str): The expected value of the most recent history entry
        """
        recent_history_items = self.get_elements("recent-history-content")
        actual_value = recent_history_items[0].get_attribute("value")
        assert actual_value == expected_value
        return self

    @BasePage.context_chrome
    def get_random_history_entry(self) -> Optional[Tuple[str, str]]:
        """
        Retrieve a random browser history entry from the Panel UI.

        This method ensures the History submenu is open, fetches all available
        history items, selects one at random, extracts its URL and title, and
        returns them after validating both are usable.
        """
        items = self.get_elements("bookmark-item")

        if not items:
            return None

        item = random.choice(items)
        raw_url = item.get_attribute("image")
        label = item.get_attribute("label")

        trimmed_url = self._extract_url_from_history(raw_url)
        assert trimmed_url and label, "History item has missing URL or label."
        return trimmed_url, label

    def _extract_url_from_history(self, raw_url: str) -> str:
        """
        Extract a valid HTTP(S) URL from a raw history image attribute. This method locates the first occurrence of
        "http" and returns the substring from there.
        Argument:
            raw_url (str): The raw string value from the 'image' attribute of a history entry.
        """
        if not raw_url:
            return ""
        if "http" in raw_url:
            return raw_url[raw_url.find("http") :]
        return raw_url.strip()

    @BasePage.context_chrome
    def confirm_history_clear(self):
        """
        Confirm that the history is empty
        """
        self.open_history_menu()
        self.element_attribute_contains("recent-history-content", "value", "(Empty)")

    @BasePage.context_chrome
    def verify_history_item_exists(self, item_title: str) -> BasePage:
        """
        Verify that a history item with the specified title exists in the history menu.

        Argument:
            item_title (str): The title text to look for in the history item (can be partial match)
        """
        self.open_history_menu()
        self.get_all_history()
        self.element_visible("panel-menu-item-by-title", labels=[item_title])
        return self

    @BasePage.context_chrome
    def verify_history_item_does_not_exist(self, item_title: str) -> BasePage:
        """
        Verify that a history item with the specified title does not exist in the history menu.

        Argument:
            item_title (str): The title text to look for in the history item (can be partial match)
        """
        self.open_history_menu()
        self.get_all_history()
        self.element_not_visible("panel-menu-item-by-title", labels=[item_title])
        return self

    # Bookmarks section

    @BasePage.context_chrome
    def open_bookmarks_panel_from_hamburger_menu(self) -> BasePage:
        """
        Opens the Bookmarks panel from the Hamburger Menu
        """
        self.open_panel_menu()
        self.click_on("panel-ui-bookmarks")
        return self

    @BasePage.context_chrome
    def bookmark_current_tab_via_hamburger_menu(self) -> BasePage:
        """
        Opens the Bookmarks panel from the Hamburger Menu, selects Bookmarks the current tab.. and clicks
        Save button from Add Bookmark in Address bar "
        """
        self.click_on("bookmark-current-tab")
        self.click_on("save-bookmark-button")
        return self

    @BasePage.context_chrome
    def verify_bookmark_exists_in_hamburger_menu(self, bookmark_title: str) -> BasePage:
        """
        Verifies that a bookmark with the specified title exists inside Bookmark section from Hamburger menu
        Arguments:
            bookmark_title (str): The title text to look for in the bookmark
        """
        self.element_visible("panel-menu-item-by-title", labels=[bookmark_title])
        return self

    @BasePage.context_chrome
    def enable_bookmark_tagging(self) -> BasePage:
        """
        Enable tagging functionality for bookmarks by executing a script
        """
        self.driver.execute_script(self.ENABLE_ADD_TAG)
        return self

    @BasePage.context_chrome
    def edit_bookmark_from_hamburger_menu(
        self, new_name: str, tags: str, location: str
    ) -> BasePage:
        """
        Edit bookmark details from hamburger menu
        """
        self.open_bookmarks_panel_from_hamburger_menu()
        self.click_on("bookmark-current-tab")

        # Edit bookmark details
        self.get_element("edit-bookmark-panel").send_keys(new_name)
        self.get_element("bookmark-tags").send_keys(tags)
        if location == "Other Bookmarks":
            self.click_on("bookmark-location")
            self.click_on("other-bookmarks")
        elif location == "Bookmarks Toolbar":
            self.click_on("bookmark-location")
            self.click_on("bookmarks-toolbar")
        self.click_on("save-bookmark-button")

    @BasePage.context_chrome
    def get_bookmark_tags(self, tags: List[str]) -> List[str]:
        """
        Returns the actual bookmark tag values from the UI
        """
        self.open_bookmarks_panel_from_hamburger_menu()
        self.click_on("bookmark-current-tab")
        self.click_on("extend-bookmark-tags")
        return [
            self.get_element(f"{tag.lower().replace(' ', '')}-tag").get_attribute(
                "value"
            )
            for tag in tags
        ]

    @BasePage.context_chrome
    def unfocus_address_bar(self) -> None:
        """
        Click away from the address bar by clicking in the new tab page content area.
        """
        locator = self.elements["toolbarspring"]["selectorData"]

        # Wait until the element is visible and clickable
        element = self.wait.until(
            EC.visibility_of_element_located((By.ID, locator)),
            message="New tab page content area not clickable.",
        )
        # Click to unfocus the address bar
        element.click()

    @BasePage.context_chrome
    def reopen_all_recently_closed_tabs(self) -> BasePage:
        """Reopen all recently closed tabs via Hamburger > History > Recently Closed."""
        self.reopen_recently_closed_tabs()
        self.element_visible("reopen-all-closed-tabs-button")
        self.click_on("reopen-all-closed-tabs-button")
        return self

    @BasePage.context_chrome
    def get_recently_closed_tab_urls(self):
        """Get URLs/labels of recently closed tabs from the Hamburger menu."""
        self.reopen_recently_closed_tabs()
        items = self.get_elements("bookmark-item")
        urls = []
        for item in items:
            if item.is_displayed():
                label = item.get_attribute("label") or ""
                urls.append(label)
        return urls

    @BasePage.context_chrome
    def verify_urls_not_in_recently_closed(self, urls: set[str]):
        """Verify that the specified URLs are not in the recently closed tabs list."""
        recently_closed = set(self.get_recently_closed_tab_urls())
        found = urls.intersection(recently_closed)
        assert len(found) == 0, (
            f"Expected URLs to be removed from recently closed, but found: {found}"
        )
