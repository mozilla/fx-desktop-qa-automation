import logging

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

    def confirm_bookmark_exists(self, match_string: str) -> BasePage:
        """
        For a given string, return self if it exists in the label of a bookmark, else assert False.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            bookmarks = self.get_elements("bookmark-in-bar")
            logging.info(f"Found {len(bookmarks)} bookmarks.")
            for el in bookmarks:
                logging.info(el.get_attribute("label"))

            matches_short_string = any(
                [match_string in el.get_attribute("label") for el in bookmarks]
            )
            matches_long_string = any(
                [el.get_attribute("label") in match_string for el in bookmarks]
            )
            assert matches_short_string or matches_long_string
            return self
