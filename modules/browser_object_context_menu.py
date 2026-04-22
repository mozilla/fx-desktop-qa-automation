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
    def click_choose_ai_chatbot_from_context_menu(self) -> BasePage:
        """Click the 'Choose an AI Chatbot' item from the AI Chat submenu in the tab context menu.

        Pure Selenium cannot interact with XUL submenu items in the chrome context: ActionChains
        move_to_element does not cross GeckoDriver's chrome context boundary, and Selenium's click()
        on a XUL <menu> element does not open its popup. JS dispatches the full mouse event sequence
        directly on the menuitem, which fires the XUL command event that opens the sidebar.
        """
        self.wait.until(
            lambda _: self.driver.execute_script(
                "const menu = document.getElementById('context_askChat');"
                "if (!menu) return false;"
                "const popup = menu.querySelector('menupopup') || menu.menupopup;"
                "if (!popup) return false;"
                "const item = popup.querySelector('[data-l10n-id=\"genai-menu-choose-chatbot\"]');"
                "if (!item) return false;"
                "item.dispatchEvent(new MouseEvent('mousemove', {bubbles: true}));"
                "item.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));"
                "item.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));"
                "item.dispatchEvent(new MouseEvent('click', {bubbles: true}));"
                "return true;"
            )
        )
        return self

    @BasePage.context_chrome
    def click_open_chatbot_from_context_menu(self) -> BasePage:
        """Click the 'Open Chatbot' item from the AI Chat submenu in the tab context menu.

        The tabContextMenu must be open before calling this (via tabs.context_click). Setting
        menu.open = true on the XUL <menu> element opens the submenu inline while the parent
        tabContextMenu is still open, which triggers provider-specific children to be generated
        in the menupopup DOM. Pure Selenium cannot hover XUL elements across GeckoDriver's chrome
        context boundary; ActionChains.move_to_element does not cross that boundary.
        """
        self.wait.until(
            lambda _: self.driver.execute_script(
                "const menu = document.getElementById('context_askChat');"
                "if (!menu) return false;"
                "menu.open = true;"
                "const popup = menu.querySelector('menupopup') || menu.menupopup;"
                "if (!popup) return false;"
                "const item = popup.querySelector('[data-l10n-id=\"genai-menu-open-provider\"]');"
                "if (!item) return false;"
                "item.dispatchEvent(new MouseEvent('mousemove', {bubbles: true}));"
                "item.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));"
                "item.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));"
                "item.dispatchEvent(new MouseEvent('click', {bubbles: true}));"
                "return true;"
            )
        )
        return self

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
