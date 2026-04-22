import logging
from typing import Dict, List, Union

from selenium.webdriver.remote.webelement import WebElement

from modules.page_base import BasePage


class ContextMenu(BasePage):
    """
    Browser Object Model (base class/parent class) for the context menus upon right clicking
    """

    URL_TEMPLATE = ""

    @BasePage.context_chrome
    def click_context_item(
        self, reference: Union[str, tuple, WebElement], labels=[]
    ) -> BasePage:
        """
        Clicks the context item.
        """

        self.fetch(reference, labels=labels).click()
        return self

    @BasePage.context_chrome
    def open_link_in_container(self) -> BasePage:
        """Open a link from the context menu in a specific container tab."""
        self.click_context_item("context-menu-open-link-in-new_container_tab")
        self.click_context_item("context-menu-open-link-in-container-work")
        return self

    @BasePage.context_chrome
    def verify_topsites_tile_context_menu_options(
        self,
        static_items: Dict[str, str],
        dynamic_items: List[str],
        tile_title: str,
    ):
        """
        Verifies expected context menu options are present upon right clicking a topsite tile.
        Arguments:
            static_items: Dict mapping of selector name to expected label text.
            dynamic_items: List of selector names for items with dynamic labels.
            tile_title: Optional, required if dynamic label validation is needed (e.g., Wikipedia, YouTube).
        """
        # --- Static items ---
        for selector, expected_label in static_items.items():
            option = self.get_element(selector)
            label = (option.get_attribute("label") or option.text or "").strip()
            assert expected_label in label, (
                f'Expected label "{expected_label}" not found. Got: "{label}"'
            )

        # --- Dynamic items ---
        for selector in dynamic_items:
            option = self.get_element(selector)
            label = (option.get_attribute("label") or option.text or "").strip()
            normalized = label.lower()
            assert normalized.startswith("search"), (
                f'Label does not start with "Search": "{label}"'
            )
            assert "for" in normalized, f'"for" not found in label: "{label}"'
            assert tile_title.lower() in normalized, (
                f'Search term "{tile_title}" not found in label: "{label}"'
            )

    @BasePage.context_chrome
    def bookmark_tab_via_context_menu(self) -> BasePage:
        """Click 'Bookmark Tab' in the tab context menu, dismiss the menu, then
        confirm the Add Bookmark dialog by clicking its Save button via JS.

        The dialog renders inside browser.dialogFrame > #document >
        dialog#bookmarkpropertiesdialog (shadow root), so JS is used to pierce
        through contentDocument and shadow DOM.
        """
        self.click_context_item("context-menu-bookmark-tab")
        self.hide_popup("tabContextMenu")
        self.wait.until(
            lambda _: self.driver.execute_script(
                "const cd = document.querySelector('browser.dialogFrame')?.contentDocument;"
                "const btn = cd?.querySelector('dialog#bookmarkpropertiesdialog')"
                "?.shadowRoot?.querySelector('button[dlgtype=\"accept\"]');"
                "if (btn) { btn.click(); return true; }"
            )
        )
        return self

    @BasePage.context_chrome
    def verify_item_disabled(self, reference: str, labels=None):
        """Assert a context menu item is disabled (grayed out)."""
        el = self.get_element(reference, labels=labels)
        assert el.get_attribute("disabled") == "true", (
            f"{reference} is not disabled"
        )


class AboutDownloadsContextMenu(ContextMenu):
    """
    Browser object model for the context menu for right clicking a download in About:Downloads
    """

    def has_all_options_available(self) -> ContextMenu:
        """Timeout unless all items labeled downloadOption are present, else return self"""
        with self.driver.context(self.context_id):
            for elname in [
                k for k, v in self.elements.items() if "downloadOption" in v["groups"]
            ]:
                logging.info(f"elname {elname}")
                self.element_exists(elname)
        return self
