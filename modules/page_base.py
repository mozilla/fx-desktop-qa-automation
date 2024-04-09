from pypom import Page

from modules.util import PomUtils


class BasePage(Page):
    def __init__(self, driver, **kwargs):
        super().__init__(driver, **kwargs)
        self.utils = PomUtils(self.driver)

    def expect(self, condition) -> Page:
        self.wait.until(condition)
        return self
