from typing import Literal

from modules.page_base import BasePage


class ForgetPanel(BasePage):
    """
    BOM for the forget panel
    """

    URL_TEMPLATE = ""

    def forget_history(
        self,
        timeframe: Literal["forget-five-minutes", "forget-two-hours", "forget-one-day"],
    ) -> BasePage:
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element(timeframe).click()
            self.get_element("forget-confirm-button").click()
            return self
