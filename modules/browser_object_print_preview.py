from selenium.common import NoAlertPresentException
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
        """Switch to the iframe holding the Print Preview settings."""
        ba = BrowserActions(self.driver)
        with self.driver.context(self.driver.CONTEXT_CHROME):
            ba.switch_to_iframe_context(self.get_element("print-settings-browser"))
            # Wait for print button to be present as indicator of readiness
            self.element_exists("print-button")
        return self

    @BasePage.context_content
    def start_print(self) -> BasePage:
        """Press Enter in Print Preview Page."""
        from pynput.keyboard import Controller, Key

        self.switch_to_preview_window()
        self.get_element("print-button").click()
        # Wait for print dialog to appear
        self.custom_wait(timeout=5).until(lambda d: _get_alert(d))
        keyboard = Controller()
        keyboard.tap(Key.enter)
        return self

    @BasePage.context_chrome
    def hover_preview(self) -> BasePage:
        """Hover over the print preview to reveal the page indicator toolbar."""
        preview_browser = self.get_element("print-preview-browser")
        self.actions.move_to_element(preview_browser).perform()
        # Wait for pagination to become visible
        self.element_visible("print-preview-pagination")
        return self

    @BasePage.context_chrome
    def wait_for_preview_ready(self, timeout: int = 20) -> BasePage:
        """Wait until Print Preview has current-page and sheet-count >= 1."""

        def _ready(_):
            preview_browser = self.get_element("print-preview-browser")
            current_page = preview_browser.get_attribute("current-page")
            sheet_count = preview_browser.get_attribute("sheet-count")
            # Return False if attributes not yet present
            if current_page is None or sheet_count is None:
                return False
            return int(sheet_count) >= 1 and int(current_page) >= 1

        self.custom_wait(timeout=timeout).until(_ready)
        return self

    @BasePage.context_chrome
    def get_sheet_indicator_values(self) -> tuple[int, int]:
        """Return (current_page, sheet_count) from print-preview-browser attributes."""
        preview_browser = self.get_element("print-preview-browser")
        current_page = preview_browser.get_attribute("current-page")
        sheet_count = preview_browser.get_attribute("sheet-count")

        assert current_page is not None, (
            "Missing 'current-page' attribute on print-preview-browser"
        )
        assert sheet_count is not None, (
            "Missing 'sheet-count' attribute on print-preview-browser"
        )

        return int(current_page), int(sheet_count)

    @BasePage.context_chrome
    def get_sheet_indicator_text(self) -> str:
        """Return a display-friendly string, e.g. '1 of 5' (derived from attributes)."""
        current, total = self.get_sheet_indicator_values()
        return f"{current} of {total}"

    @BasePage.context_chrome
    def _wait_for_current_page(self, expected: int, timeout: int = 15) -> None:
        """Wait until current-page equals expected."""
        self.custom_wait(timeout=timeout).until(
            lambda _: self.get_sheet_indicator_values()[0] == expected
        )

    @BasePage.context_chrome
    def _click_pagination_button(self, button_name: str) -> None:
        """
        Click a navigation button in the print preview pagination toolbar.
        button_name: 'navigateHome', 'navigatePrevious', 'navigateNext', 'navigateEnd'
        """
        self.hover_preview()
        pagination = self.get_element("print-preview-pagination")
        # Access shadow root via JavaScript and click button (parameterized for safety)
        self.driver.execute_script(
            "arguments[0].shadowRoot.getElementById(arguments[1]).click()",
            pagination,
            button_name,
        )

    @BasePage.context_chrome
    def go_to_first_page(self) -> BasePage:
        """Click << (navigateHome) and verify we reached page 1."""
        self.wait_for_preview_ready()
        current, _total = self.get_sheet_indicator_values()

        if current != 1:
            self._click_pagination_button("navigateHome")
            self._wait_for_current_page(expected=1)

        current, _total = self.get_sheet_indicator_values()
        assert current == 1, "Failed to navigate to first page in Print Preview"
        return self

    @BasePage.context_chrome
    def go_to_previous_page(self) -> BasePage:
        """Click < (navigatePrevious) and verify page decremented when possible."""
        self.wait_for_preview_ready()
        before, _total = self.get_sheet_indicator_values()

        self._click_pagination_button("navigatePrevious")

        expected = max(1, before - 1)
        self._wait_for_current_page(expected=expected)

        current, _total = self.get_sheet_indicator_values()
        assert current == expected, "Failed to go to previous page"
        return self

    @BasePage.context_chrome
    def go_to_next_page(self) -> BasePage:
        """Click > (navigateNext) and verify page incremented when possible."""
        self.wait_for_preview_ready()
        before, total = self.get_sheet_indicator_values()

        self._click_pagination_button("navigateNext")

        expected = min(total, before + 1)
        self._wait_for_current_page(expected=expected)

        current, _total = self.get_sheet_indicator_values()
        assert current == expected, "Failed to go to next page"
        return self

    @BasePage.context_chrome
    def go_to_last_page(self) -> BasePage:
        """Click >> (navigateEnd) and verify we reached the last page."""
        self.wait_for_preview_ready()
        _current, total = self.get_sheet_indicator_values()

        self._click_pagination_button("navigateEnd")
        self._wait_for_current_page(expected=total)

        current, _total = self.get_sheet_indicator_values()
        assert current == total, "Failed to navigate to last page in Print Preview"
        return self
