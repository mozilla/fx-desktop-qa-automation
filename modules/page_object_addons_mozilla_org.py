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
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.driver.find_element(By.CSS_SELECTOR, "button[label='Add']").click()
            self.driver.find_element(By.CSS_SELECTOR, "button[label='Okay']").click()
        return self
