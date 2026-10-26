from selenium.webdriver.common.keys import Keys

from .browser_object_panel_ui import PanelUi
from .page_base import BasePage


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

    @BasePage.context_chrome
    def click_primary_button(self) -> BasePage:
        """
        Click the primary action button in the print settings dialog.

        With the "Mozilla Save to PDF" destination this button is labelled
        "Save" and opens the native file picker (nsIFilePicker); install a mock
        file picker beforehand to capture the save location.

        The print settings live in a XUL <browser> (printSettingsBrowser) whose
        content cannot be entered with Selenium frame switching, so the button
        is clicked through the browser's contentDocument, the same way
        _click_pagination_button reaches through the shadow root.
        """
        settings_browser = self.get_element("print-settings-browser")
        self.custom_wait(timeout=10).until(
            lambda _: self.driver.execute_script(
                "return !!arguments[0].contentDocument"
                "?.getElementById('print-button');",
                settings_browser,
            )
        )
        self.driver.execute_script(
            "arguments[0].contentDocument.getElementById('print-button').click();",
            settings_browser,
        )
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
    def _wait_for_current_page(self, expected: int, timeout: int = 20):
        """Wait until current-page equals expected."""
        self.custom_wait(timeout=timeout).until(
            lambda _: self.get_sheet_indicator_values()[0] == expected
        )

    @BasePage.context_chrome
    def _click_pagination_button(self, button_id: str):
        """
        Click a navigation button in the print preview pagination toolbar.
        button_id: 'navigateHome', 'navigatePrevious', 'navigateNext', 'navigateEnd'

        Note: Uses JavaScript to access shadow DOM because the buttons are nested
        deep within the shadow root. The framework's find_shadow_element only
        searches direct children, but shadowRoot.getElementById() finds at any depth.
        """
        self.hover_preview()
        pagination = self.get_element("print-preview-pagination")
        self.driver.execute_script(
            "arguments[0].shadowRoot.getElementById(arguments[1]).click()",
            pagination,
            button_id,
        )

    @BasePage.context_chrome
    def go_to_first_page(self) -> BasePage:
        """Click << (navigateHome) and wait until we reach page 1."""
        self.wait_for_preview_ready()
        current, _total = self.get_sheet_indicator_values()
        if current != 1:
            self._click_pagination_button("navigateHome")
            self._wait_for_current_page(expected=1)
        return self

    @BasePage.context_chrome
    def go_to_previous_page(self) -> BasePage:
        """Click < (navigatePrevious) and wait for page to decrement."""
        self.wait_for_preview_ready()
        before, _total = self.get_sheet_indicator_values()
        self._click_pagination_button("navigatePrevious")
        self._wait_for_current_page(expected=max(1, before - 1))
        return self

    @BasePage.context_chrome
    def go_to_next_page(self) -> BasePage:
        """Click > (navigateNext) and wait for page to increment."""
        self.wait_for_preview_ready()
        before, total = self.get_sheet_indicator_values()
        self._click_pagination_button("navigateNext")
        self._wait_for_current_page(expected=min(total, before + 1))
        return self

    @BasePage.context_chrome
    def go_to_last_page(self) -> BasePage:
        """Click >> (navigateEnd) and wait until we reach the last page."""
        self.wait_for_preview_ready()
        _current, total = self.get_sheet_indicator_values()
        self._click_pagination_button("navigateEnd")
        self._wait_for_current_page(expected=total)
        return self

    @BasePage.context_chrome
    def _set_settings_control(self, element_id: str, value: str) -> None:
        """Set a print-settings control and dispatch the event used by the UI."""
        settings_browser = self.get_element("print-settings-browser")
        self.driver.execute_script(
            """
            const element = arguments[0].contentDocument.getElementById(arguments[1]);
            if (!element) throw new Error(`Missing print setting: ${arguments[1]}`);
            element.value = arguments[2];
            element.dispatchEvent(new Event("input", { bubbles: true }));
            """,
            settings_browser,
            element_id,
            value,
        )

    @BasePage.context_chrome
    def select_page_range(self, value: str) -> BasePage:
        """Select a page-range option such as 'all' or 'custom'."""
        self._set_settings_control("range-picker", value)
        self.custom_wait(timeout=10).until(
            lambda _: self.custom_page_range_is_visible() == (value == "custom")
        )
        return self

    @BasePage.context_chrome
    def set_custom_page_range(self, page_range: str) -> BasePage:
        """Select Custom pages and enter a range such as '4-6,9'"""
        settings_browser = self.get_element("print-settings-browser")

        self.custom_wait(timeout=20).until(
            lambda _: self.driver.execute_script(
                """
                const input = arguments[0].contentDocument.getElementById("custom-range");
                return input && !input.disabled;
                """,
                settings_browser,
            )
        )
        self._set_settings_control("range-picker", "custom")

        self.custom_wait(timeout=10).until(
            lambda _: self.driver.execute_script(
                """
                const input = arguments[0].contentDocument.getElementById("custom-range");
                return input && !input.hidden;
                """,
                settings_browser,
            )
        )
        self._set_settings_control("custom-range", page_range)
        return self

    @BasePage.context_chrome
    def custom_page_range_is_visible(self) -> bool:
        """Return whether the custom page-range input is visible."""
        settings_browser = self.get_element("print-settings-browser")
        return self.driver.execute_script(
            """
            const input = arguments[0].contentDocument.getElementById("custom-range");
            return !!input && !input.hidden;
            """,
            settings_browser,
        )

    @BasePage.context_chrome
    def wait_for_sheet_count(self, expected: int, timeout: int = 20) -> BasePage:
        """Wait until PrintPreview shows the expected number of sheets"""
        self.custom_wait(timeout=timeout).until(
            lambda _: self.get_sheet_indicator_values()[1] == expected
        )
        return self

    @BasePage.context_chrome
    def expect_invalid_custom_page_range(self, timeout: int = 10) -> BasePage:
        """Wait for the custom-range error and verify the print form is invalid"""
        settings_browser = self.get_element("print-settings-browser")

        self.custom_wait(timeout=timeout).until(
            lambda _: self.driver.execute_script(
                """
                const doc = arguments[0].contentDocument;
                const input = doc.getElementById("custom-range");
                const error = doc.getElementById("error-invalid-range");
                const form = doc.getElementById("print");

                return input
                    && error
                    && form
                    && !error.hidden
                    && !input.validity.valid
                    && !form.checkValidity()
                """,
                settings_browser,
            ),
            message="Expected the invalid-range error and an invalid print form.",
        )
        return self
