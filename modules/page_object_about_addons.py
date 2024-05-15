from modules.browser_object import Navigation
from modules.page_base import BasePage


class AboutAddons(BasePage):
    """
    The POM for the about:addons page
    """

    URL_TEMPLATE = "about:addons"

    themes = ["", "", ""]

    def choose_sidebar_option(self, *label):
        self.get_element("sidebar-options", *label).click()

    def activate_theme(self, nav: Navigation, theme_name: str, intended_color: str):
        # for theme in self.themes:
        self.get_element("theme-card", theme_name).click()
        self.get_element("enable-theme").click()
        # verify the css
        awesome_bar = nav.get_awesome_bar()
        background_colour = awesome_bar.value_of_css_property("background-color")
        print(background_colour)
        assert background_colour == intended_color

        # itr += 1
