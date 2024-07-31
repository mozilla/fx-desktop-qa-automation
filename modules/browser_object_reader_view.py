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
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("reader-view-button").click()
        self.wait_for_reader_view_open()
        return self

    def open_reader_view_keys(self) -> BasePage:
        """
        Opens the reader view using keys
        """
        if self.sys_platform() == "Darwin":
            self.actions.key_down(Keys.COMMAND).key_down(Keys.ALT).send_keys(
                "r"
            ).key_up(Keys.ALT).key_up(Keys.COMMAND).perform()
        elif self.sys_platform() == "Linux":
            self.actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys(
                "r"
            ).key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
        else:
            self.actions.send_keys(Keys.F9).perform()
        self.wait_for_reader_view_open()
        return self

    def close_reader_view_searchbar(self) -> BasePage:
        """
        Closes the reader view using the search bar
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("reader-view-button").click()
        self.wait_for_reader_view_closed()
        return self

    def close_reader_view_keys(self, sys_platform: str) -> BasePage:
        """
        Closes the reader view using keys
        """
        if sys_platform == "Darwin":
            self.actions.key_down(Keys.COMMAND).key_down(Keys.ALT).send_keys(
                "r"
            ).key_up(Keys.ALT).key_up(Keys.COMMAND).perform()
        elif sys_platform == "Linux":
            self.actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys(
                "r"
            ).key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
        else:
            self.actions.send_keys(Keys.F9).perform()
        self.wait_for_reader_view_closed()
        return self

    def wait_for_reader_view_open(self) -> BasePage:
        """
        Checks to see if the reader view toolbar is present demonstrating that the reader view is open.
        """
        self.wait.until(lambda _: self.element_exists("reader-toolbar"))
        return self

    def wait_for_reader_view_closed(self) -> BasePage:
        """
        Checks to see if the reader view toolbar is not present, demonstrating that reader view is not open.
        """
        self.wait.until(lambda _: self.element_does_not_exist("reader-toolbar"))
        return self
