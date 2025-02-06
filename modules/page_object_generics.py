from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

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
        return self

    def zoom_out_keys(self) -> BasePage:
        if self.sys_platform() == "Darwin":
            self.perform_key_combo(Keys.COMMAND, "-")
        else:
            self.perform_key_combo(Keys.CONTROL, "-")
        return self

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

    def fill_element(self, element: str, data: str) -> BasePage:
        """fill in the field at element with data"""
        self.get_element(element).send_keys(data)
        return self

    def click_download_button(self) -> BasePage:
        """click on download button for the pdf"""
        self.get_element("download-button").click()
        self.wait_for_page_to_load()
        return self

    def select_and_return_checkbox(self, element: str) -> WebElement:
        """select checkbox located at element"""
        checkbox = self.get_element(element)
        checkbox.click()
        return checkbox

    def select_and_return_dropdown_option(
        self, element: str, selector: By, value: str
    ) -> WebElement:
        """click dropdown element and select dropdown option through selector"""
        self.get_element(element).click()
        dropdown_option = self.find_element(selector, value)
        dropdown_option.click()
        return dropdown_option
