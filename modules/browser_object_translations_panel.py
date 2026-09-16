from modules.page_base import BasePage


class TranslationsPanel(BasePage):
    """
    BOM for the full page translations panel
    """

    URL_TEMPLATE = ""

    def open_panel(self) -> BasePage:
        """
        Open the translations panel from the URL bar button.

        The button only shows up after the page language is detected.
        """
        self.element_visible("translations-urlbar-button")
        self.click_on("translations-urlbar-button")
        self.element_visible("translations-panel")
        return self

    def check_always_translate_language(self) -> BasePage:
        """
        Open the settings wheel gear menu and check "Always translate <language>".
        """
        self.click_on("settings-gear-button")
        self.element_visible("always-translate-menuitem")
        self.click_on("always-translate-menuitem")

        # autocheck="false", so Firefox adds the attribute once the pref is set.
        self.expect(
            lambda _: (
                self.get_element("always-translate-menuitem").get_attribute("checked")
                is not None
            )
        )
        return self
