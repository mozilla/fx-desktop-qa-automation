from .page_base import BasePage

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

    @BasePage.context_chrome
    def _pointer_click(self, reference: str) -> BasePage:
        """
        Click with a pointer action, for moz-buttons in the panel.
        """
        # Marionette's native click can't scroll a moz-button in a panel into view.
        self.actions.move_to_element(self.get_element(reference)).click().perform()
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
    def translate_page(self, timeout: int = TRANSLATION_TIMEOUT) -> BasePage:
        """
        Press Translate in the panel and wait until the page is translated.

        Args:
            timeout: Seconds to wait for the translation
        """
        self._pointer_click("panel-translate-button")

        # The language badge only shows up once the engine is done.
        self.custom_wait(timeout=timeout).until(
            lambda _: self.get_element(
                "translations-urlbar-button-locale"
            ).is_displayed()
        )
        return self

    def check_always_translate_language(self) -> BasePage:
        """
        Open the settings wheel gear menu and check "Always translate <language>".
        """
        self._pointer_click("settings-gear-button")
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

    def check_never_translate_language(self) -> BasePage:
        """
        Open the settings wheel gear menu and check "Never translate <language>".
        """
        self._pointer_click("settings-gear-button")
        self.element_visible("never-translate-menuitem")
        self.click_on("never-translate-menuitem")

        # autocheck="false", so Firefox adds the attribute once the pref is set.
        self.expect(
            lambda _: (
                self.get_element("never-translate-menuitem").get_attribute("checked")
                is not None
            )
        )
        return self

    def check_never_translate_site(self) -> BasePage:
        """
        Open the settings wheel gear menu and check "Never translate this site".
        """
        self._pointer_click("settings-gear-button")
        self.element_visible("never-translate-site-menuitem")
        self.click_on("never-translate-site-menuitem")

        # autocheck="false", so Firefox adds the attribute once the permission is set.
        self.expect(
            lambda _: (
                self.get_element("never-translate-site-menuitem").get_attribute(
                    "checked"
                )
                is not None
            )
        )
        return self
