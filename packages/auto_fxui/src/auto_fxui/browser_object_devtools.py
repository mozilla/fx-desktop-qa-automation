from .page_base import BasePage


class Devtools(BasePage):
    """BOM for the DevTools panel"""

    URL_TEMPLATE = ""

    def check_opened(self) -> BasePage:
        self.wait_for_page_to_load()
        return self

    @BasePage.context_chrome
    def get_console_messages(self) -> list[str]:
        """Return every message logged to the browser console."""
        return self.driver.execute_script(
            "return Services.console.getMessageArray().map(m => m.message);"
        )

    def console_contains(self, text: str) -> bool:
        return any(text in msg for msg in self.get_console_messages())

    def expect_console_contains(self, text: str) -> BasePage:
        """Wait until a browser console message contains text."""
        self.expect(lambda _: self.console_contains(text))
        return self

    @BasePage.context_chrome
    def clear_console(self) -> BasePage:
        self.driver.execute_script("Services.console.reset();")
        return self
