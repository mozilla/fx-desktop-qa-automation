from pypom import Region
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from modules.page_base import BasePage
from modules.util import PomUtils


class PanelUi(BasePage):
    """Page Object Model for nav panel UI menu (hamburger menu, application menu)"""

    URL_TEMPLATE = "about:blank"

    class Menu(Region):
        def __init__(self, page, **kwargs):
            super().__init__(page, **kwargs)
            self.utils = PomUtils(self.driver)

        @property
        def loaded(self):
            targeted = [el for el in self.page.elements.values() if "requiredForPage" in el["groups"] and "menuItem" in el["groups"]]
            return all(
                [EC.presence_of_element_located(el) for el in targeted]
            )


    def open_panel_menu(self) -> BasePage:
        with self.driver.context(self.driver.CONTEXT_CHROME):
            with open("pre_menu_open.html", "w") as fh:
                fh.write(self.driver.page_source)
            panel_root = self.get_element("panel-ui-button")
            panel_root.click()
            with open("menu_content.html", "w") as fh:
                fh.write(self.driver.page_source)
            self.menu = self.Menu(self, root=panel_root)
        return self
