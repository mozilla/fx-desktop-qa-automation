from modules.page_base import BasePage


class Devtools(BasePage):
    """BOM for the DevTools panel"""

    URL_TEMPLATE = ""

    def check_opened(self) -> BasePage:
        self.wait_for_page_to_load()
        return self
