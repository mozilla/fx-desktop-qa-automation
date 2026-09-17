from modules.page_base import BasePage

TRANSLATIONS_PARENT_MODULE = "resource://gre/actors/TranslationsParent.sys.mjs"
# First run downloads the language model, which is slow.
TRANSLATION_TIMEOUT = 120


class TranslationsPanel(BasePage):
    """
    BOM for the full page translations panel
    """

    URL_TEMPLATE = ""

    @BasePage.context_chrome
    def allow_automatic_popup(self) -> BasePage:
        """
        Let the panel open on its own when Firefox offers a translation.

        TranslationsParent suppresses the automatic popup whenever Marionette
        is running, so the test flag has to be set to get the real behaviour.
        """
        # Flip the product's own test flag; there is no pref for this.
        self.driver.execute_script(
            f"""
            const {{ TranslationsParent }} = ChromeUtils.importESModule(
                "{TRANSLATIONS_PARENT_MODULE}"
            );
            TranslationsParent.testAutomaticPopup = true;
            """
        )
        return self

    def open_panel(self) -> BasePage:
        """
        Open the translations panel from the URL bar button.

        The button only shows up after the page language is detected.
        """
        self.element_visible("translations-urlbar-button")
        self.click_on("translations-urlbar-button")
        self.element_visible("translations-panel")
        return self

    @BasePage.context_chrome
    def translate_page(self) -> BasePage:
        """
        Press Translate in the panel and wait until the page is translated.
        """
        self.click_on("panel-translate-button")

        # The language badge only shows up once the engine is done.
        self.custom_wait(timeout=TRANSLATION_TIMEOUT).until(
            lambda _: self.get_element(
                "translations-urlbar-button-locale"
            ).is_displayed()
        )
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
