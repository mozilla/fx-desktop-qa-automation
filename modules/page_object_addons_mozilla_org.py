from selenium.webdriver.common.by import By

from modules.page_base import BasePage

# PLEASE add all AMO page models to this file


class AmoThemes(BasePage):
    """
    POM for AMO Themes
    """

    URL_TEMPLATE = "https://addons.mozilla.org/en-US/firefox/themes"

    def install_recommended_theme(self) -> BasePage:
        """
        Install the first recommended theme.
        """
        self.get_element("recommended-addon").click()
        self.theme_title = self.get_element("theme-title").get_attribute("innerText")
        self.get_element("install-button").click()
        # TODO: Add toolbar browser object
        # with self.driver.context(self.driver.CONTEXT_CHROME):
        #     self.driver.find_element(By.CSS_SELECTOR, "button[label='Add']").click()
        #     self.driver.find_element(By.CSS_SELECTOR, "button[label='OK']").click()
        # return self

    @BasePage.context_chrome
    def confirm_language_install_popup(self):
        """Confirms the language install popup by clicking Add then OK"""
        # Wait for the Add button to appear
        self.custom_wait(timeout=10).until(
            lambda _: self.get_element("addon-install-add-button-parent") is not None
        )

        # Click "Add" button
        self.js_click_on("addon-install-add-button-field")

        # Wait for the OK button to appear
        self.custom_wait(timeout=10).until(
            lambda _: self.get_element("addon-install-ok-button-parent") is not None
        )

        # Click "OK" button
        self.js_click_on("addon-install-ok-button-field")
        return self

class AmoLanguages(BasePage):
    """
    POM for AMO Languages
    """

    URL_TEMPLATE = "https://addons.mozilla.org/en-US/firefox/language-tools/"

    def wait_for_language_page_to_load(self) -> BasePage:
        """
        Waits until the language page is loaded
        """
        self.custom_wait(timeout=20).until(
            lambda _: self.get_element("language-addons-title") is not None
        )
        return self

    def find_language_row_and_navigate(self, language_label: str) -> BasePage:
        """
        Finds the row that corresponds with the language_label and clicks into it
        """
        language_row = self.get_element("language-addons-row", labels=[language_label])
        self.get_element(
            "language-addons-row-link", parent_element=language_row
        ).click()

        # ensuring the subpage of the language is loaded
        self.custom_wait(timeout=20).until(
            lambda _: self.get_element("language-addons-subpage-header") is not None
        )
        return self

    @BasePage.context_chrome
    def confirm_language_install_popup(self):
        """Confirms the language install popup by clicking Add then OK"""
        # Click "Add" button
        self.js_click_on("addon-install-add-button-field")

        # Wait for the OK button to appear
        self.custom_wait(timeout=10).until(
            lambda _: self.get_element("addon-install-ok-button-parent") is not None
        )

        # Click "OK" button
        self.js_click_on("addon-install-ok-button-field")
        return self
