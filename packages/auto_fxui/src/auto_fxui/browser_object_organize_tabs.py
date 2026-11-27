from selenium.webdriver.common.action_chains import ActionChains

from .page_base import BasePage

AUTO_TAB_GROUPING_MODULE = "moz-src:///browser/components/aiwindow/ui/modules/AutoTabGroupingSuggestions.sys.mjs"


class OrganizeTabs(BasePage):
    """Browser Object Model for the Smart Window Organize Tabs button, panel and flyout."""

    URL_TEMPLATE = "about:blank"

    @BasePage.context_chrome
    def stub_clusters(self, groups: list[list[str]]) -> BasePage:
        """Make clustering return one cluster per list of tab URLs in `groups`."""
        # Firefox can't download the embedding model under automation, so this replaces the one ML step.
        error = self.driver.execute_script(
            f"""
            const {{ AutoTabGroupingSuggestions }} = ChromeUtils.importESModule(
              "{AUTO_TAB_GROUPING_MODULE}"
            );
            const manager = AutoTabGroupingSuggestions.manager;
            if (typeof manager.generateClusters !== "function") {{
              return "SmartTabGroupingManager.generateClusters is missing; "
                + "Firefox changed how Organize Tabs clusters tabs";
            }}
            const groups = arguments[0];
            manager.generateClusters = async tabs => ({{
              clusterRepresentations: groups.map(urls => ({{
                tabs: tabs.filter(t => urls.includes(t.linkedBrowser.currentURI.spec)),
                cohesion: 1,
              }})),
            }});
            return null;
            """,
            groups,
        )
        assert not error, error
        return self

    @BasePage.context_chrome
    def is_button_shown(self) -> bool:
        """Report whether the Organize Tabs button is on the tab strip and visible."""
        return bool(
            self.driver.execute_script(
                """
                const b = document.getElementById("smartwindow-group-tabs-button");
                return !!b && !b.hidden && b.checkVisibility();
                """
            )
        )

    @BasePage.context_chrome
    def expect_button_shown(self) -> BasePage:
        """Wait until the Organize Tabs button is offered."""
        self.wait.until(
            lambda _: self.is_button_shown(),
            message="The Organize Tabs button is not shown",
        )
        return self

    @BasePage.context_chrome
    def open_panel(self) -> BasePage:
        """Click the Organize Tabs button and wait for the panel to open."""
        self.expect_button_shown()
        self.click_on("organize-tabs-button")
        self.wait.until(
            lambda _: self.get_element("panel").get_attribute("state") == "open",
            message="The Organize Tabs panel did not open",
        )
        return self

    @BasePage.context_chrome
    def expect_suggestions(self, count: int) -> BasePage:
        """Wait until the panel lists `count` suggested groups."""
        self.wait.until(
            lambda _: len(self.get_elements("suggestion-rows")) == count,
            message=f"The panel did not list {count} suggested groups",
        )
        return self

    @BasePage.context_chrome
    def hover_suggestion(self, index: int = 0) -> BasePage:
        """Hover a suggested group so the flyout lists its tabs."""
        row = self.get_elements("suggestion-rows")[index]
        ActionChains(self.driver).move_to_element(row).perform()
        return self

    @BasePage.context_chrome
    def get_flyout_tab_titles(self) -> list[str]:
        """Wait for the flyout to open and return the tab titles it lists."""
        self.wait.until(
            lambda _: self.get_element("flyout").get_attribute("state") == "open"
            and self.get_elements("flyout-tabs"),
            message="The flyout did not list any tabs",
        )
        return [tab.get_attribute("title") for tab in self.get_elements("flyout-tabs")]

    @BasePage.context_chrome
    def create_suggested_group(self, index: int = 0) -> BasePage:
        """Click a suggested group to create it."""
        # Selenium's own click can't scroll rows in a popup into view.
        row = self.get_elements("suggestion-rows")[index]
        ActionChains(self.driver).move_to_element(row).click().perform()
        return self

    @BasePage.context_chrome
    def expect_recent_groups(self, count: int) -> BasePage:
        """Wait until the Just created section lists `count` groups."""
        self.wait.until(
            lambda _: len(self.get_elements("recent-rows")) == count,
            message=f"The Just created section did not list {count} groups",
        )
        return self

    @BasePage.context_chrome
    def click_ungroup(self) -> BasePage:
        """Click Ungroup Tabs, which undoes the groups just created."""
        button = self.get_element("ungroup-button")
        ActionChains(self.driver).move_to_element(button).click().perform()
        return self
