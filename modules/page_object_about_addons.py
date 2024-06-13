from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation
from modules.page_base import BasePage


class AboutAddons(BasePage):
    """
    The POM for the about:addons page

    Attributes
    ----------
    driver: selenium.webdriver.Firefox
        WebDriver object under test
    """

    URL_TEMPLATE = "about:addons"

    def choose_sidebar_option(self, option: str):
        """
        Clicks the corresponding sidebar option from the about:addons page.
        """
        self.get_element("sidebar-options", labels=[option]).click()

    def activate_theme(
        self, nav: Navigation, theme_name: str, intended_color: str, perform_assert=True
    ):
        """
        Clicks the theme card and presses enable. Then verifies that the theme is the correct color.

        Attributes
        ----------
        nav: Navigation
            The navgiation object
        theme_name: str
            The name of the theme to press
        intended_color: str
            The RGB string that is the intended color of the element
        """
        self.get_element("theme-card", labels=[theme_name]).click()
        self.get_element("enable-theme").click()

        self.expect(
            EC.text_to_be_present_in_element_attribute(
                self.get_selector("enable-theme"), "innerText", "Disable"
            )
        )

        with self.driver.context(self.driver.CONTEXT_CHROME):
            navigation_component = nav.get_element("navigation-background-component")
            background_color = navigation_component.value_of_css_property(
                "background-color"
            )
            if perform_assert:
                assert background_color == intended_color
            else:
                return background_color

    def enabled_theme_matches(self, expected_theme: str) -> bool:
        """
        Check the enabled theme name against any string.
        """

        enabled_theme = self.get_element("enabled-theme-title").get_attribute(
            "innerText"
        )
        return enabled_theme == expected_theme

    def check_theme_has_changed(self, original_theme: str) -> BasePage:
        """
        Ensure that the theme has changed.
        """
        assert not self.enabled_theme_matches(original_theme)
        return self
