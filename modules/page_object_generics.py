from selenium.webdriver.common.keys import Keys

from modules.page_base import BasePage


class GenericPage(BasePage):
    """
    Generic POM for a page we don't care to map
    """

    URL_TEMPLATE = "{url}"


class GenericPdf(BasePage):
    """
    Generic POM for any page with an open PDF in it.
    """

    URL_TEMPLATE = "{pdf_url}"

    def get_green_highlighted_text(self) -> str:
        return self.get_element("highlighted-text").get_attribute("innerText")

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

    def jump_to_page(self, page_number: int) -> BasePage:
        page_input = self.get_element("page-input")
        self.double_click(page_input)
        page_input.send_keys(Keys.BACK_SPACE + str(page_number) + Keys.ENTER)
        return self

    def open_toolbar_menu(self) -> BasePage:
        self.get_element("toolbar-toggle").click()
        self.element_visible("toolbar-container")
        return self
