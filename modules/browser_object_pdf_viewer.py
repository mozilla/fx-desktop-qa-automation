from selenium.webdriver.common.keys import Keys

from modules.page_base import BasePage


class PdfViewer(BasePage):
    """
    BOM for PDF viewer
    """

    URL_TEMPLATE = ""

    def zoom_in_toolbar(self) -> BasePage:
        self.get_element("zoom-in").click()
        return self

    def zoom_out_toolbar(self) -> BasePage:
        self.get_element("zoom-out").click()
        return self

    def zoom_in_keys(self) -> BasePage:
        if self.sys_platform() == "Darwin":
            self.perform_key_combo(Keys.COMMAND, "+")
        else:
            self.perform_key_combo(Keys.CONTROL, "+")

    def zoom_out_keys(self) -> BasePage:
        if self.sys_platform() == "Darwin":
            self.perform_key_combo(Keys.COMMAND, "-")
        else:
            self.perform_key_combo(Keys.CONTROL, "-")
