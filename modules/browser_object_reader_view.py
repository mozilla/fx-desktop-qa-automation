from selenium.webdriver import Keys

from modules.page_base import BasePage


class ReaderView(BasePage):
    """
    BOM for reader view
    """

    URL_TEMPLATE = ""

    def open_reader_view_searchbar(self) -> BasePage:
        """
        Opens the reader view using the search bar
        """
        before_page_source = self.driver.page_source
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("reader-view-button").click()
        self.wait.until(lambda _: self.driver.page_source != before_page_source)
        self.wait_for_reader_view_open()
        return self

    def open_reader_view_keys(self) -> BasePage:
        """
        Opens the reader view using keys
        """
        before_page_source = self.driver.page_source
        with self.driver.context(self.driver.CONTEXT_CHROME):
            if self.sys_platform() == "Darwin":
                self.perform_key_combo(Keys.COMMAND, Keys.ALT, "r")
            elif self.sys_platform() == "Linux":
                self.perform_key_combo(Keys.CONTROL, Keys.ALT, "r")
            else:
                self.perform_key_combo(Keys.F9)
        self.wait.until(lambda _: self.driver.page_source != before_page_source)
        self.wait_for_reader_view_open()
        return self

    def close_reader_view_searchbar(self) -> BasePage:
        """
        Closes the reader view using the search bar
        """
        before_page_source = self.driver.page_source
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("reader-view-button").click()
        self.wait.until(lambda _: self.driver.page_source != before_page_source)
        self.wait_for_reader_view_closed()
        return self

    def close_reader_view_keys(self) -> BasePage:
        """
        Closes the reader view using keys
        """
        before_page_source = self.driver.page_source
        with self.driver.context(self.driver.CONTEXT_CHROME):
            if self.sys_platform() == "Darwin":
                self.perform_key_combo(Keys.COMMAND, Keys.ALT, "r")
            elif self.sys_platform() == "Linux":
                self.perform_key_combo(Keys.CONTROL, Keys.ALT, "r")
            else:
                self.perform_key_combo(Keys.F9)
        self.wait.until(lambda _: self.driver.page_source != before_page_source)
        self.wait_for_reader_view_closed()
        return self

    def wait_for_reader_view_open(self) -> BasePage:
        """
        Checks to see if the reader view toolbar is present demonstrating that the reader view is open.
        """
        self.element_exists("reader-toolbar")
        return self

    def wait_for_reader_view_closed(self) -> BasePage:
        """
        Checks to see if the reader view toolbar is not present, demonstrating that reader view is not open.
        """
        self.element_does_not_exist("reader-toolbar")
        return self

    def click_toolbar_option(self, option: str) -> BasePage:
        """
        Clicks on the toolbar option
        """
        toolbar_option = self.get_element(option)
        # self.element_clickable(option)
        toolbar_option.click()
        return self

    def open_advanced_options(self) -> BasePage:
        """
        Assuming the type panel is already open, this method will press the advanced accordian
        """
        self.get_element("toolbar-advanced").click()
        self.element_clickable("toolbar-text-align-left")
        return self
