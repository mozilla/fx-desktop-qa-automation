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
    def get_menu_item_label(self, selector: str) -> str:
        """
        Returns the label text of a context menu item, normalized.
        """
        el = self.get_element(selector)
        return (el.get_attribute("label") or el.text or "").strip()

    @BasePage.context_chrome
    def verify_topsites_tile_context_menu_options(
        self,
        static_items: Dict[str, str],
        dynamic_items: List[str],
        tile_title: str,
    ):
        """
        Verifies expected context menu items are visible and optionally checks label match.
        Arguments:
            static_items: Dict mapping of selector name to expected label text.
            dynamic_items: List of selector names for items with dynamic labels.
            tile_title: Optional, required if dynamic label validation is needed (e.g., Wikipedia, YouTube).
        """
        # --- Static items ---
        for selector, expected_label in static_items.items():
            option = self.get_element(selector)
            label = (option.get_attribute("label") or option.text or "").strip()
            print(f"[DEBUG] Static label for {selector}: {label}")
            assert expected_label in label, (
                f'Expected label "{expected_label}" not found. Got: "{label}"'
            )

        # --- Dynamic items ---
        for selector in dynamic_items:
            option = self.get_element(selector)
            label = (option.get_attribute("label") or option.text or "").strip()
            normalized = label.lower()
            print(f"[DEBUG] Dynamic label for {selector}: {label}")
            assert normalized.startswith("search"), (
                f'Label does not start with "Search": "{label}"'
            )
            assert "for" in normalized, f'"for" not found in label: "{label}"'
            assert tile_title.lower() in normalized, (
                f'Search term "{tile_title}" not found in label: "{label}"'
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
