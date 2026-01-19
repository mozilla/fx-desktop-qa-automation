from typing import cast

from modules.page_base import BasePage


class FirefoxView(BasePage):
    """
    Page Object Model for about:firefoxview.

    Note: This class will use mostly JavaScript (execute_script) instead of standard Selenium selectors because
    Firefox View elements are nested inside multiple shadow DOMs. Selenium cannot traverse more than one level of
    shadow DOM, so we use JS to pierce through the nested shadow roots and access the target elements.
    """

    URL_TEMPLATE = "about:firefoxview"

    def open_recently_closed_section(self):
        """Navigate to the Recently Closed section in Firefox View."""
        self.driver.get("about:firefoxview#recentlyclosed")
        self.wait.until(
            lambda _: self.driver.execute_script(
                "const deck = document.querySelector('named-deck');"
                "return !!deck && deck.getAttribute('selected-view') === 'recentlyclosed';"
            )
            is True
        )
        return self

    def get_recently_closed_tab_urls(self) -> list[str]:
        """Return the list of URLs shown in the Recently Closed tab rows."""
        return cast(
            list[str],
            self.driver.execute_script(
                """
                const view = document.querySelector("view-recentlyclosed[slot='selected']")
                    || document.querySelector("view-recentlyclosed");
                if (!view?.shadowRoot) return [];
                const list = view.shadowRoot.querySelector("fxview-tab-list");
                if (!list?.shadowRoot) return [];
                return Array.from(list.shadowRoot.querySelectorAll("fxview-tab-row"))
                    .map(row => row.shadowRoot?.querySelector("a.fxview-tab-row-main")?.getAttribute("href"))
                    .filter(Boolean);
                """
            ),
        )
