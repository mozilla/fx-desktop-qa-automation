from pypom import Page
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC


class Navigation(Page):
    """Page Object Model for nav buttons and AwesomeBar"""

    URL_TEMPLATE = "about:blank"
    BROWSER_MODES = {
        "Bookmarks": "*",
        "Tabs": "%",
        "History": "^",
        "Actions": ">",
    }

    _awesome_bar = (By.ID, "urlbar-input")
    _xul_source_snippet = (
        'xmlns:xul="http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul"'
    )

    # Tab-to-search
    _tab_to_search_text_span = (
        By.CLASS_NAME,
        "urlbarView-dynamic-onboardTabToSearch-text-container",
    )
    _search_mode_span = (By.ID, "urlbar-search-mode-indicator-title")

    # Overflow menu
    _overflow_item = (
        By.CSS_SELECTOR,
        '[class="urlbarView-title urlbarView-overflowable"]',
    )

    # Search Mode One-Offs
    _search_one_off_settings_button = (By.ID, "urlbar-anon-search-settings")

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

    def ensure_chrome_context(self):
        if self._xul_source_snippet not in self.driver.page_source:
            self.driver.set_context(self.driver.CONTEXT_CHROME)

    def resume_content_context(self):
        if self._xul_source_snippet in self.driver.page_source:
            self.driver.set_context(self.driver.CONTEXT_CONTENT)

    def expect(self, condition) -> Page:
        self.wait.until(condition)
        return self

    def expect_in_content(self, condition) -> Page:
        with self.driver.context(self.driver.CONTEXT_CONTENT):
            self.expect(condition)
        return self

    def get_awesome_bar(self) -> Page:
        self.ensure_chrome_context()
        self.awesome_bar = self.driver.find_element(*self._awesome_bar)
        return self

    def type_in_awesome_bar(self, term: str) -> Page:
        self.get_awesome_bar()
        self.awesome_bar.click()
        self.awesome_bar.send_keys(term)
        return self

    def set_search_mode_via_awesome_bar(self, mode: str) -> Page:
        if mode in self.BROWSER_MODES:
            abbr = self.BROWSER_MODES[mode]
        else:
            abbr = mode.lower()[:2]
        self.type_in_awesome_bar(abbr)
        self.wait.until(EC.visibility_of_element_located(self._tab_to_search_text_span))
        self.awesome_bar.send_keys(Keys.TAB)
        self.wait.until(EC.text_to_be_present_in_element(self._search_mode_span, mode))
        return self

    def search(self, term: str, mode=None) -> Page:
        self.ensure_chrome_context()
        if mode is not None:
            self.set_search_mode_via_awesome_bar(mode).type_in_awesome_bar(
                term + Keys.ENTER
            )
        else:
            self.type_in_awesome_bar(term + Keys.ENTER)
        self.resume_content_context()
        return self

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
