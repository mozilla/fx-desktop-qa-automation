from time import sleep

from selenium.webdriver.support import expected_conditions as EC

from modules.page_base import BasePage


class Toolbar(BasePage):
    """BOM for the toolbar, other than the awesome bar and the panel UI"""

    URL_TEMPLATE = ""

    def wait_for_item_to_download(self, filename: str) -> BasePage:
        """Check the downloads tool in the toolbar to wait for a given file to download"""
        original_timeout = self.driver.timeouts.implicit_wait
        try:
            # Whatever our timeout, we want to lengthen it because downloads
            self.driver.implicitly_wait(original_timeout * 2)
            self.element_visible("downloads-item-by-file", labels=[filename])
            self.expect_not(
                EC.element_attribute_to_include(
                    self.get_selector("downloads-button"), "animate"
                )
            )
            with self.driver.context(self.context_id):
                self.driver.execute_script(
                    "arguments[0].setAttribute('hidden', true)",
                    self.get_element("downloads-button"),
                )
        finally:
            self.driver.implicitly_wait(original_timeout)

        return self
