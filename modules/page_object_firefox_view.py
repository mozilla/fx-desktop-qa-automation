from typing import cast

from modules.page_base import BasePage


class FirefoxView(BasePage):
    """
    Page Object Model for about:firefoxview.

    Note: This class uses JavaScript (execute_script) instead of standard Selenium selectors because
    Firefox View elements are nested inside multiple shadow DOMs. Selenium cannot traverse more than
    one level of shadow DOM, so we use JS to pierce through the nested shadow roots.
    """

    URL_TEMPLATE = "about:firefoxview"

    def open_recently_closed(self) -> "FirefoxView":
        """Navigate to the Recently Closed section in Firefox View."""
        self.driver.get(f"{self.URL_TEMPLATE}#recentlyclosed")
        self.wait.until(lambda _: self._is_recently_closed_selected())
        return self

    def _is_recently_closed_selected(self) -> bool:
        """Check if the Recently Closed section is currently selected."""
        return bool(
            self.driver.execute_script(
                """
                const deck = document.querySelector("named-deck");
                return !!deck && deck.getAttribute("selected-view") === "recentlyclosed";
                """
            )
        )

    def get_closed_tab_urls(self) -> list[str]:
        """Return the list of URLs shown in the Recently Closed tab rows."""
        urls = self.driver.execute_script(
            """
            const view = document.querySelector("view-recentlyclosed[slot='selected']")
                || document.querySelector("view-recentlyclosed");
            if (!view?.shadowRoot) return [];

            const list = view.shadowRoot.querySelector("fxview-tab-list");
            if (!list?.shadowRoot) return [];

            const rows = Array.from(list.shadowRoot.querySelectorAll("fxview-tab-row"));
            const hrefs = [];
            for (const row of rows) {
                const root = row.shadowRoot;
                if (!root) continue;
                const a = root.querySelector("a.fxview-tab-row-main");
                const href = a && a.getAttribute("href");
                if (typeof href === "string" && href.length) hrefs.push(href);
            }
            return hrefs;
            """
        )
        return cast(list[str], urls)

    def wait_for_closed_tabs_with_urls(self, expected_urls: set[str]) -> None:
        """Wait until the expected URLs appear in the Recently Closed section."""
        self.wait.until(
            lambda _: expected_urls.issubset(set(self.get_closed_tab_urls()))
        )
