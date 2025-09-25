from typing import Literal

from modules.page_base import BasePage


class ForgetPanel(BasePage):
    """
    BOM for the Forget Panel
    """

    URL_TEMPLATE = ""

    def select_timeframe(
        self,
        timeframe: Literal["forget-five-minutes", "forget-two-hours", "forget-one-day"],
    ) -> "ForgetPanel":
        """
        Select a specific timeframe option in the forget panel.
        This will click the option regardless of what's currently selected.

        Argument:
            timeframe: Timeframe to forget. Restricted options to "forget-five-minutes",
                      "forget-two-hours", or "forget-one-day"
        """
        self.click_on(timeframe)
        return self

    def forget_history(
        self,
        timeframe: Literal["forget-five-minutes", "forget-two-hours", "forget-one-day"],
    ) -> "ForgetPanel":
        """
        Forget browsing history for a given timeframe.
        """
        self.select_timeframe(timeframe)
        self.click_on("forget-confirm-button")
        return self
