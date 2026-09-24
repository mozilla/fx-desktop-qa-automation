import json
import logging

from selenium.webdriver import Firefox

from modules.page_base import BasePage


class SmartWindowFirstRun(BasePage):
    """
    Page Object Model for the Smart Window first-run onboarding, shown at
    chrome://browser/content/aiwindow/firstrun.html after signing in through
    the Smart Window flow. It is reached through that flow, not opened directly.

    Models are picked by the brand name shown on their tile (e.g. "Gemini"),
    or left to the first offered model when the test doesn't depend on which.
    The names, their order and their choice ids come from the server, so the
    choice id is read from the page when the tile is picked.
    """

    def __init__(self, driver: Firefox, **kwargs):
        super().__init__(driver, **kwargs)
        self.model_choice_id: str | None = None

    def get_offered_models(self) -> list[str]:
        """Return the brand names of the models offered, in display order"""
        self.element_visible("model-label")
        return [
            json.loads(label.get_attribute("data-l10n-args"))["brandName"]
            for label in self.get_elements("model-label")
        ]

    def select_model(self, name: str) -> BasePage:
        """
        Pick a model tile by brand name and remember its choice id.

        Parameters
        ----------
        name : str
            The model's brand name as shown on its tile, e.g. "Gemini".
        """
        offered = self.get_offered_models()
        assert name in offered, (
            f"Model '{name}' is not offered; available: {', '.join(offered)}"
        )
        self.click_on("model-tile", labels=[name])
        self.element_selected("model-radio", labels=[name])
        value = self.get_element("model-radio", labels=[name]).get_attribute("value")
        self.model_choice_id = value.removeprefix("model_")
        return self

    def expect_model_choice_saved(self) -> BasePage:
        """Wait until Firefox has saved the model picked in select_model"""
        assert self.model_choice_id is not None, (
            "Call select_model() before expect_model_choice_saved()"
        )
        self.expect(
            lambda _: self.get_pref("browser.smartwindow.firstrun.modelChoice")
            == self.model_choice_id
        )
        return self

    def complete_onboarding(self, model_name: str | None = None) -> BasePage:
        """
        Go through onboarding with a model and the default choices on the
        later screens.

        Parameters
        ----------
        model_name : str | None
            The model's brand name as shown on its tile, e.g. "Gemini". Leave
            out when the test doesn't depend on the model; the first offered
            model is picked, so a server-side rename or reorder can't break it.
        """
        self.element_visible("choose-model-screen")
        if model_name is None:
            model_name = self.get_offered_models()[0]
            logging.info(f"No model requested; picking the first offered: {model_name}")
        self.select_model(model_name)
        self.element_clickable("next-button")
        self.click_on("next-button")
        self.element_visible("memories-screen")
        self.click_on("continue-button")
        self.element_visible("set-default-screen")
        self.click_on("continue-button")
        return self
