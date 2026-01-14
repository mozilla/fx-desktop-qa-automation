from time import sleep

from selenium.common import NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from modules.browser_object_panel_ui import PanelUi
from modules.page_base import BasePage
from modules.util import BrowserActions


def _get_alert(d):
    try:
        alert = d.switch_to.alert
    except NoAlertPresentException:
        return False
    return alert


class PrintPreview(BasePage):
    """Browser Object Model for Print Preview modal"""

    def __init__(self, driver):
        super().__init__(driver)
        self.panel_ui = PanelUi(self.driver)

    URL_TEMPLATE = "about:blank"

    @BasePage.context_chrome
    def open_and_load_print_from_panelui(self) -> BasePage:
        """Use PanelUi to open the Print Preview, wait for element to load"""
        self.panel_ui.open_panel_menu()
        self.panel_ui.click_on("print-option")
        self.wait_for_page_to_load()
        return self

    @BasePage.context_chrome
    def open_with_key_combo(self) -> BasePage:
        """Use Cmd/Ctrl + P to open the Print Preview, wait for load"""

        if self.sys_platform() == "Darwin":
            mod_key = Keys.COMMAND
        else:
            mod_key = Keys.CONTROL
        self.perform_key_combo(mod_key, "p")
        self.wait_for_page_to_load()
        return self

    def switch_to_preview_window(self) -> BasePage:
        """Switch to the iframe holding the Print Preview"""
        ba = BrowserActions(self.driver)
        sleep(3)
        with self.driver.context(self.driver.CONTEXT_CHROME):
            ba.switch_to_iframe_context(self.get_element("print-settings-browser"))
            self.expect(
                lambda _: self.driver.execute_script(
                    'return document.readyState === "complete";'
                )
            )
        return self

    @BasePage.context_content
    def start_print(self) -> BasePage:
        """Press Enter in Print Preview Page."""
        from pynput.keyboard import Controller, Key

        self.switch_to_preview_window()
        self.get_element("print-button").click()
        sleep(2)
        keyboard = Controller()
        keyboard.tap(Key.enter)
        return self

    @BasePage.context_chrome
    def hover_preview(self) -> BasePage:
        """Hover over the print preview to reveal the page indicator toolbar."""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            preview_browser = self.get_element("print-preview-browser")
            self.actions.move_to_element(preview_browser).perform()
            sleep(0.5)
        return self

    @BasePage.context_chrome
    def wait_for_preview_ready(self, timeout: int = 20) -> BasePage:
        """Wait until Print Preview is loaded with page count."""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            # Wait for sheet-count attribute to be present and > 0
            self.custom_wait(timeout=timeout).until(
                lambda _: self.get_element("print-preview-browser").get_attribute(
                    "sheet-count"
                )
            )

    def get_sheet_indicator_text(self) -> str:
        """Return the text from the page indicator, for example: '1 of 5'."""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            preview_browser = self.get_element("print-preview-browser")
            current_page = preview_browser.get_attribute("current-page")
            sheet_count = preview_browser.get_attribute("sheet-count")
            return f"{current_page} of {sheet_count}"

    def _parse_sheet_indicator(self) -> tuple[int, int]:
        """
        Parse 'X of Y' into (X, Y).
        Returns (current, total). Raises AssertionError if format is unexpected.
        """
        text = self.get_sheet_indicator_text().strip()

        # Expected format is localized, but for en-US it's "1 of 5".
        # If l10n changes, you can fall back to data-l10n-args instead.
        if " of " not in text:
            raise AssertionError(f"Unexpected sheet indicator format: '{text}'")

        left, right = text.split(" of ", 1)
        current = int(left.strip())
        total = int(right.strip())
        return current, total

    def debug_pagination_shadow_dom(self) -> str:
        """Debug helper: returns the innerHTML of pagination shadow DOM."""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            pagination = self.get_element("print-preview-pagination")
            return self.driver.execute_script(
                "return arguments[0].shadowRoot.innerHTML", pagination
            )

    def _click_pagination_button(self, button_name: str) -> None:
        """
        Click a navigation button in the print preview pagination toolbar.
        button_name: 'navigateHome', 'navigatePrevious', 'navigateNext', 'navigateEnd'
        """
        self.hover_preview()
        with self.driver.context(self.driver.CONTEXT_CHROME):
            pagination = self.get_element("print-preview-pagination")
            # Access shadow root via JavaScript and click button
            self.driver.execute_script(
                f"arguments[0].shadowRoot.getElementById('{button_name}').click()",
                pagination,
            )
            sleep(0.5)

    def go_to_first_page(self) -> BasePage:
        """Click << (navigateHome) and verify we reached page 1."""
        self.wait_for_preview_ready()
        current, _total = self._parse_sheet_indicator()

        if current > 1:
            self._click_pagination_button("navigateHome")

        current, _total = self._parse_sheet_indicator()
        assert current == 1, "Failed to navigate to first page in Print Preview"
        return self

    def go_to_previous_page(self) -> BasePage:
        """Click < (navigatePrevious) and verify page decremented when possible."""
        self.wait_for_preview_ready()
        before_current, _total = self._parse_sheet_indicator()

        self._click_pagination_button("navigatePrevious")

        current, _total = self._parse_sheet_indicator()
        if before_current > 1:
            assert current == before_current - 1, "Failed to go to previous page"
        else:
            assert current == 1, "Page should stay at 1 when already on first page"

        return self

    def go_to_next_page(self) -> BasePage:
        """Click > (navigateNext) and verify page incremented when possible."""
        self.wait_for_preview_ready()
        before_current, total = self._parse_sheet_indicator()

        self._click_pagination_button("navigateNext")

        current, _total = self._parse_sheet_indicator()
        if before_current < total:
            assert current == before_current + 1, "Failed to go to next page"
        else:
            assert current == total, (
                "Page should stay at last when already on last page"
            )

        return self

    def go_to_last_page(self) -> BasePage:
        """Click >> (navigateEnd) and verify we reached the last page."""
        self.wait_for_preview_ready()
        current, total = self._parse_sheet_indicator()

        if current < total:
            self._click_pagination_button("navigateEnd")

        current, total = self._parse_sheet_indicator()
        assert current == total, "Failed to navigate to last page in Print Preview"
        return self
