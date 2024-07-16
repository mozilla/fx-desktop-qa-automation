from pypom import Region
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from modules.page_base import BasePage
from modules.util import PomUtils


class PanelUi(BasePage):
    """Page Object Model for nav panel UI menu (hamburger menu, application menu)"""

    URL_TEMPLATE = "about:blank"

    class Menu(Region):
        """
        PyPOM Region factory for the PanelUi Dropdown menu
        """

        def __init__(self, page, **kwargs):
            super().__init__(page, **kwargs)
            self.utils = PomUtils(self.driver)

        @property
        def loaded(self):
            targeted = [
                el
                for el in self.page.elements.values()
                if "requiredForPage" in el["groups"] and "menuItem" in el["groups"]
            ]
            return all([EC.presence_of_element_located(el) for el in targeted])

    def open_panel_menu(self) -> BasePage:
        """
        Opens the PanelUi menu.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            panel_root = self.get_element("panel-ui-button")
            panel_root.click()
            self.menu = self.Menu(self, root=panel_root)
        return self

    def select_panel_setting(self, name: str, *labels) -> BasePage:
        """
        Selects a panel setting in PanelUi.

        ...

        Parameters
        ----------

        name: str
            Name of setting element
        labels: *list[str]
            Labels to pass to get_element()
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            panel_option = self.get_element(name, labels=labels)
            panel_option.click()
        return self

    def navigate_to_about_addons(self):
        """
        On the hamburger menu > More Tools > Customize Toolbar > Manage Themes
        """
        self.select_panel_setting("more-tools")
        self.select_panel_setting("customize-toolbar")
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("manage-themes").click()

    def navigate_to_customize_toolbar(self):
        """
        On the hamburger menu > More Tools > Customize Toolbar
        """
        self.select_panel_setting("more-tools")
        self.select_panel_setting("customize-toolbar")

    def click_sync_sign_in_button(self) -> BasePage:
        """
        Click FxA sync button.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.open_panel_menu()
            self.select_panel_setting("fxa-sign-in")
        return self

    def log_out_fxa(self) -> BasePage:
        """
        Click FxA signout button.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.click_sync_sign_in_button()
            self.get_element("fxa-sign-out-button").click()
        return self

    def manage_fxa_account(self) -> BasePage:
        """
        Open the FxA management flow.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.click_sync_sign_in_button()
            self.get_element("fxa-manage-account-button").click()
        return self

    def confirm_sync_in_progress(self) -> BasePage:
        """
        Check that FxA Sync Label is set to "Syncing…"
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.click_sync_sign_in_button()
            try:
                self.instawait.until(
                    EC.text_to_be_present_in_element(
                        self.get_selector("fxa-sync-label"), "Sync"
                    )
                )
            except (NoSuchElementException, TimeoutException):
                self.get_element("panel-ui-button").click()
                self.click_sync_sign_in_button()
            self.custom_wait(timeout=30, poll_frequency=0.5).until(
                EC.text_to_be_present_in_element(
                    self.get_selector("fxa-sync-label"), "Syncing"
                )
            )
        return self

    def start_sync(self) -> BasePage:
        """
        Start FxA sync
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.click_sync_sign_in_button()
            self.element_has_text("fxa-sync-label", "Sync now")
            self.get_element("fxa-sync-label").click()
        return self

    def open_private_window(self) -> BasePage:
        """
        Opens a new window in private browsing mode using the panel
        """
        self.open_panel_menu()
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("panel-ui-new-private-window").click()
        return self
