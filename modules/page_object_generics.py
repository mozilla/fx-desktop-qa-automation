from time import sleep

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

    def add_image(self, image_path: str, sys_platform: str) -> BasePage:
        self.get_element("toolbar-add-image").click()
        self.get_element("toolbar-add-image-confirm").click()
        sleep(3)
        from pynput.keyboard import Controller, Key

        keyboard = Controller()
        if sys_platform == "Darwin" or sys_platform == "Linux":
            keyboard.type("/")
            sleep(3)
            keyboard.type(image_path.lstrip("/"))
        else:
            sleep(2)
            keyboard.type(image_path)
        sleep(1)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        sleep(2)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        return self
