from dataclasses import dataclass
from pypom import Page, Region
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Firefox
from selenium.webdriver.common import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.exceptions import (
    WebDriverException,
    InvalidArgumentException,
)


class PomUtils:
    def __init__(self, driver: Firefox):
        self.driver = driver

    def get_shadow_content(self, element: WebElement) -> list[WebElement]:
        try:
            shadow_root = element.shadow_root
            return [shadow_root]
        except InvalidArgumentException:
            shadow_children = driver.execute_script(
                "return arguments[0].shadowRoot.children", element
            )
            if len(shadow_children) and shadow_children[0] is not None:
                return shadow_children


class AboutPrefs(Page):
    """Page Object Model for about:preferences"""

    self.utils = PomUtils(self.driver)
    _category_search = (By.ID, "category-search")
    _search_engine_dropdown = (By.ID, "defaultEngine")

    def get_dropdown(self, selector: tuple[str, str]) -> self.Dropdown:
        menu_root = self.driver.find_element(*selector)
        return Dropdown(self, menu_root)

    def get_dropdown_by_current_value(self, value: str) -> self.Dropdown:
        menu_root = self.driver.find_element(
            By.CSS_SELECTOR, f"menulist[label='{value}']"
        )
        return Dropdown(self, menu_root)

    def get_dropdown_by_label(self, label: str) -> self.Dropdown:
        menu_root = self.driver.find_element(
            By.XPATH,
            f".//label[contains(., '{label}')]/following-sibling::hbox/menulist",
        )
        return Dropdown(self, menu_root)

    # Misc

    class Dropdown(Region):
        _active_dropdown_item = (By.CSS_SELECTOR, "menuitem[_moz-menuactive='true']")

        def __init__(self, root):
            self.root = root
            self.utils = PomUtils(self.root)
            shadow_elements = self.utils.get_shadow_content(self.root)
            self.dropmarker = next(
                e for e in shadow_elements if e.tag_name == "dropmarker"
            )

        @property
        def loaded(self):
            return self.dropmarker if self.dropmarker else False

        def select_option(self, option_name):
            menu_open = lambda: self.dropmarker.get_attribute("open") == "true"
            if not menu_open():
                self.root.click()
            matching_menuitems = [
                e
                for e in self.root.find_elements(By.CSS_SELECTOR, "menuitem")
                if e.get_attribute("innerText").lower() == option_name.lower()
            ]
            if len(matching_menuitems) == 0:
                return False
            elif len(matching_menuitems) == 1:
                matching_menuitems[0].click()
                return matching_menuitems[0]
            else:
                raise ValueError("More than one menu item matched search string")


@dataclass
class AboutGlean:
    """Page Object Model for about:glean"""

    # Elements
    ping_id_input = (By.ID, "tag-pings")
    submit_button = (By.ID, "controls-submit")


@dataclass
class Navigation:
    """Page Object Model for nav buttons and AwesomeBar"""

    awesome_bar = (By.ID, "urlbar-input")

    # Tab-to-search
    tab_to_search_text_span = (
        By.CLASS_NAME,
        "urlbarView-dynamic-onboardTabToSearch-text-container",
    )
    search_mode_span = (By.ID, "urlbar-search-mode-indicator-title")

    # Overflow menu
    overflow_item = (
        By.CSS_SELECTOR,
        '[class="urlbarView-title urlbarView-overflowable"]',
    )

    # Search Mode One-Offs
    search_one_off_settings_button = (By.ID, "urlbar-anon-search-settings")

    def search_one_off_engine_button(self, site):
        return (
            By.CSS_SELECTOR,
            f"[id*=urlbar-engine-one-off-item-engine][tooltiptext^={site}]",
        )

    def search_one_off_browser_button(self, source):
        return (
            By.ID,
            f"urlbar-engine-one-off-item-{source}",
        )

    # "Refresh Firefox" incl. Intervention Card
    quick_actions_refresh_button = (By.ID, "urlbarView-row-3-label-0")
    refresh_intervention_card = (
        By.CSS_SELECTOR,
        'div[tip-type="intervention_refresh"]',
    )
    fx_refresh_text = (
        By.CSS_SELECTOR,
        'span[data-l10n-id="intervention-refresh-profile"]',
    )
    fx_refresh_button = (
        By.CSS_SELECTOR,
        'span[role="button"][data-l10n-id="intervention-refresh-profile-confirm"]',
    )
    fx_refresh_menu = (
        By.CSS_SELECTOR,
        'span[data-l10n-id="urlbar-result-menu-button"][title="Open menu"]',
    )
    fx_refresh_menu_get_help_item = (
        By.CSS_SELECTOR,
        'menuitem[data-l10n-id="urlbar-result-menu-tip-get-help"]',
    )

    # Search with...
    search_engine_suggestion_row = (
        By.CSS_SELECTOR,
        'div[class="urlbarView-row"][type="search_engine"]',
    )


# Endnotes:
#  - If you're looking for about:logins, that page has so many shadow DOMs
#    that all elements exist in shadow_dom.py.
