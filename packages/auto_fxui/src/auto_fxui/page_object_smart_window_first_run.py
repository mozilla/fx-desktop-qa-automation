import json
import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from .page_base import BasePage

# The single-page onboarding's controls, by id, in Tab order.
ONBOARDING_CONTROLS = ("model", "memories", "default-window", "save")

UTILS_MODULE = "moz-src:///browser/components/aiwindow/models/Utils.sys.mjs"


class SmartWindowFirstRun(BasePage):
    """
    Page Object Model for the Smart Window first-run onboarding, shown at
    chrome://browser/content/aiwindow/firstrun.html after signing in through
    the Smart Window flow. Tests that aren't about sign-in open it with
    SmartWindow.open_first_run().

    Firefox shows one of two layouts: the single-page onboarding when
    browser.smartwindow.firstrun.singlePageWithAutoModel is true (the default
    from Firefox 163), otherwise a series of screens. The methods below work
    with either.

    Models are picked by brand name (e.g. "Gemini", or "Auto"), or left to the
    first offered model when the test doesn't depend on which. The names,
    their order and their choice ids come from the server, so the choice id is
    read from the page when a model is picked.
    """

    def __init__(self, driver: Firefox, **kwargs):
        super().__init__(driver, **kwargs)
        self.model_choice_id: str | None = None

    @BasePage.context_chrome
    def get_pref(self, name: str) -> bool | int | str | None:
        """
        Return the current value of a Firefox pref, or None if it is not set.

        Parameters
        ----------
        name : str
            The pref name, e.g. "browser.smartwindow.firstrun.modelChoice".
        """
        return self.driver.execute_script(
            """
            const name = arguments[0];
            switch (Services.prefs.getPrefType(name)) {
              case Services.prefs.PREF_BOOL:
                return Services.prefs.getBoolPref(name);
              case Services.prefs.PREF_INT:
                return Services.prefs.getIntPref(name);
              case Services.prefs.PREF_STRING:
                return Services.prefs.getStringPref(name);
              default:
                return null;
            }
            """,
            name,
        )

    def is_single_page(self) -> bool:
        """Wait for the first run to render and report whether it is the single-page layout."""
        self.expect(
            lambda _: self.driver.execute_script(
                "return !!document.querySelector("
                "'smartwindow-onboarding, main.screen.AI_WINDOW_CHOOSE_MODEL');"
            )
        )
        return bool(self.driver.find_elements(*self.get_selector("onboarding")))

    @BasePage.context_chrome
    def _model_brand_names(self) -> dict[str, str]:
        """Return each model choice id's brand name, with "Auto" for the Auto model."""
        return self.driver.execute_script(
            f"""
            return (async () => {{
              const {{ AUTO_MODEL_CHOICE_ID, getAllModelsData }} =
                ChromeUtils.importESModule("{UTILS_MODULE}");
              const names = {{ [AUTO_MODEL_CHOICE_ID]: "Auto" }};
              for (const [id, model] of Object.entries(await getAllModelsData())) {{
                names[id] = model.brandName;
              }}
              return names;
            }})();
            """
        )

    def expect_setup_screen(self) -> BasePage:
        """Wait until the single-page onboarding has moved past its welcome section."""
        self.element_visible("setup-screen")
        return self

    def _open_model_menu(self) -> BasePage:
        self.expect_setup_screen()
        self.click_on("model-select-button")
        self.expect(lambda _: self.get_elements("model-options"))
        self.element_visible("model-options")
        return self

    def _close_model_menu(self) -> BasePage:
        self.click_on("model-select-button")
        self.element_not_visible("model-options")
        return self

    def get_selected_model(self) -> str:
        """Return the brand name of the model the single-page onboarding has selected."""
        self.expect_setup_screen()
        choice_id = self.get_element("model-select").get_attribute("value")
        return self._model_brand_names()[choice_id]

    def get_offered_models(self) -> list[str]:
        """Return the brand names of the models offered, in display order"""
        if self.is_single_page():
            self._open_model_menu()
            choice_ids = [
                option.get_attribute("data-value")
                for option in self.get_elements("model-options")
            ]
            self._close_model_menu()
            names = self._model_brand_names()
            return [names[choice_id] for choice_id in choice_ids]
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
        if self.is_single_page():
            choice_id = {
                brand: choice_id
                for choice_id, brand in self._model_brand_names().items()
            }[name]
            self._open_model_menu()
            self.click_on("model-option", labels=[choice_id])
            self.element_attribute_is("model-select", "value", choice_id)
            self.model_choice_id = choice_id
            return self
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
            lambda _: (
                self.get_pref("browser.smartwindow.firstrun.modelChoice")
                == self.model_choice_id
            )
        )
        return self

    def is_default_window_on(self) -> bool:
        """Report whether the single-page onboarding's Start in Smart Window toggle is on."""
        self.expect_setup_screen()
        return bool(self.get_element("default-window-toggle").get_property("pressed"))

    def set_default_window(self, on: bool) -> BasePage:
        """Turn the single-page onboarding's Start in Smart Window toggle on or off."""
        if self.is_default_window_on() != on:
            self.click_on("default-window-toggle-button")
        self.expect(lambda _: self.is_default_window_on() == on)
        return self

    def save(self) -> BasePage:
        """Click the single-page onboarding's Let's go button."""
        self.expect_setup_screen()
        self.click_on("save-button")
        return self

    def complete_onboarding(self, model_name: str | None = None) -> BasePage:
        """
        Go through onboarding with a model and the default choices for the
        rest.

        Parameters
        ----------
        model_name : str | None
            The model's brand name as shown on its tile, e.g. "Gemini". Leave
            out when the test doesn't depend on the model; the first offered
            model is picked, so a server-side rename or reorder can't break it.
        """
        single_page = self.is_single_page()
        if not single_page:
            self.element_visible("choose-model-screen")
        if model_name is None:
            model_name = self.get_offered_models()[0]
            logging.info(f"No model requested; picking the first offered: {model_name}")
        self.select_model(model_name)
        if single_page:
            return self.save()
        self.element_clickable("next-button")
        self.click_on("next-button")
        self.element_visible("memories-screen")
        self.click_on("continue-button")
        self.element_visible("set-default-screen")
        self.click_on("continue-button")
        return self

    # ── Keyboard ─────────────────────────────────────────────────────────

    def _read_onboarding(self, body: str, *args):
        """Run `body` in the page with `root`, the single-page onboarding's shadow root."""
        return self.driver.execute_script(
            "const host = document.querySelector('smartwindow-onboarding');"
            "const root = host && host.shadowRoot;" + body,
            *args,
        )

    def get_focused_control(self) -> str | None:
        """Return which of ONBOARDING_CONTROLS has keyboard focus, or None."""
        focused = self._read_onboarding(
            "const el = root && root.activeElement; return el ? el.id : null;"
        )
        return focused if focused in ONBOARDING_CONTROLS else None

    def tab_to_control(self, name: str) -> BasePage:
        """Press Tab until the single-page onboarding's control `name` has focus."""
        self.expect_setup_screen()
        # Tab also leaves the page and returns, so allow a full lap.
        for _ in range(len(ONBOARDING_CONTROLS) * 2 + 1):
            if self.get_focused_control() == name:
                return self
            self.actions.send_keys(Keys.TAB).perform()
            try:
                self.custom_wait(timeout=1, poll_frequency=0.1).until(
                    lambda _: self.get_focused_control() == name
                )
            except TimeoutException:
                pass
        raise AssertionError(f"Tab never reached the {name} control")

    def get_option_value(self, name: str) -> str:
        """Return the value of the onboarding's `model` or `memories` dropdown."""
        return self._read_onboarding(
            "return root.querySelector('#' + arguments[0]).value;", name
        )

    def choose_other_option_with_keyboard(self, name: str) -> str:
        """
        Open the focused `model` or `memories` dropdown with Enter, arrow to an
        option other than the current one, pick it with Enter and return its value.
        """
        before = self.get_option_value(name)
        self.actions.send_keys(Keys.ENTER).perform()

        def _focused_option() -> str | None:
            return self._read_onboarding(
                "const el = root.querySelector('#' + arguments[0]).shadowRoot.activeElement;"
                "return el && el.matches('button.option-item') ? el.dataset.value : null;",
                name,
            )

        self.expect(lambda _: _focused_option() is not None)
        options = self._read_onboarding(
            "return root.querySelector('#' + arguments[0]).shadowRoot"
            ".querySelectorAll('button.option-item').length;",
            name,
        )
        for _ in range(options):
            if _focused_option() != before:
                break
            self.actions.send_keys(Keys.ARROW_DOWN).perform()
            try:
                self.custom_wait(timeout=1, poll_frequency=0.1).until(
                    lambda _: _focused_option() != before
                )
            except TimeoutException:
                pass
        chosen = _focused_option()
        assert chosen and chosen != before, f"The arrow keys stayed on {before}"
        self.actions.send_keys(Keys.ENTER).perform()
        self.expect(lambda _: self.get_option_value(name) == chosen)
        self.expect(lambda _: self.get_focused_control() == name)
        return chosen
