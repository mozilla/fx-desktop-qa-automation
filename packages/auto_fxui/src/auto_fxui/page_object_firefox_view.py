from typing import cast

from .page_base import BasePage


class FirefoxView(BasePage):
    """
    Page Object Model for about:firefoxview.

    Note: This class uses JavaScript (execute_script) instead of standard Selenium selectors because
    Firefox View elements are nested inside multiple shadow DOMs. Selenium cannot traverse more than
    one level of shadow DOM, so we use JS to pierce through the nested shadow roots.
    """

    URL_TEMPLATE = "about:firefoxview"

    def open_recently_closed(self) -> BasePage:
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

    def wait_for_closed_tabs_with_urls(self, expected_urls: set[str]) -> BasePage:
        """Wait until the expected URLs appear in the Recently Closed section."""
        self.wait.until(
            lambda _: expected_urls.issubset(set(self.get_closed_tab_urls()))
        )
        return self

    def wait_for_no_closed_tabs(self) -> BasePage:
        """Wait until the Recently Closed section has no tab entries."""
        self.wait.until(lambda _: len(self.get_closed_tab_urls()) == 0)
        return self

    # ── History and Chats views ──────────────────────────────────────────

    def _open_view_in_new_tab(self, view: str) -> BasePage:
        """Open about:firefoxview#<view> in a new selected tab and switch to it."""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.driver.execute_script(
                """
                gBrowser.selectedTab = gBrowser.addTrustedTab(
                  "about:firefoxview#" + arguments[0]
                );
                """,
                view,
            )
        self.switch_to_new_tab()
        self.wait.until(lambda _: self._selected_view() == view)
        return self

    def _selected_view(self) -> str | None:
        return self.driver.execute_script(
            """
            const deck = document.querySelector("named-deck");
            return deck && deck.getAttribute("selected-view");
            """
        )

    def open_history(self) -> BasePage:
        """Open the History view of Firefox View in a new tab."""
        return self._open_view_in_new_tab("history")

    def open_chats(self) -> BasePage:
        """Open the Chats view of Firefox View in a new tab (Smart Window only)."""
        return self._open_view_in_new_tab("chats")

    def _read_rows(self, view_tag: str, row_tag: str) -> list[dict]:
        return self.driver.execute_script(
            """
            const [viewTag, rowTag] = arguments;
            const view = document.querySelector(viewTag);
            if (!view || !view.shadowRoot) return [];
            const rows = [];
            for (const list of view.shadowRoot.querySelectorAll(rowTag.replace("row", "list"))) {
              if (!list.shadowRoot) continue;
              for (const row of list.shadowRoot.querySelectorAll(rowTag)) {
                const link = row.shadowRoot && row.shadowRoot.querySelector("a.fxview-tab-row-main");
                const title = row.shadowRoot && row.shadowRoot.querySelector("#fxview-tab-row-title");
                if (!link) continue;
                rows.push({
                  url: link.getAttribute("href"),
                  id: link.getAttribute("data-conv-id"),
                  title: title ? title.textContent.trim() : "",
                });
              }
            }
            return rows;
            """,
            view_tag,
            row_tag,
        )

    def get_history_entries(self) -> list[dict]:
        """Return the History entries shown, each with url and title."""
        return self._read_rows("view-history", "fxview-tab-row")

    def get_chat_entries(self) -> list[dict]:
        """Return the chats shown in the Chats view, each with id and title."""
        return self._read_rows("view-chats", "chats-tab-row")

    def get_history_urls(self) -> list[str]:
        return [entry["url"] for entry in self.get_history_entries()]

    def get_chat_ids(self) -> list[str]:
        return [entry["id"] for entry in self.get_chat_entries()]

    def expect_history_urls(self, urls: list[str]) -> BasePage:
        """Wait until every URL in `urls` is listed in History."""
        self.wait.until(lambda _: set(urls).issubset(self.get_history_urls()))
        return self

    def expect_chats(self, ids: list[str]) -> BasePage:
        """Wait until every conversation id in `ids` is listed in Chats."""
        self.wait.until(lambda _: set(ids).issubset(self.get_chat_ids()))
        return self

    def _open_row_menu(self, view_tag: str, row_tag: str, key: str, value: str) -> bool:
        """Click a row's options button; False if the row isn't listed."""
        return bool(
            self.driver.execute_script(
                """
                const [viewTag, rowTag, key, value] = arguments;
                const view = document.querySelector(viewTag);
                const lists = view.shadowRoot.querySelectorAll(rowTag.replace("row", "list"));
                for (const list of lists) {
                  for (const row of list.shadowRoot.querySelectorAll(rowTag)) {
                    const link = row.shadowRoot.querySelector("a.fxview-tab-row-main");
                    if (!link) continue;
                    const found = key === "id"
                      ? link.getAttribute("data-conv-id")
                      : link.getAttribute("href");
                    if (found !== value) continue;
                    row.shadowRoot.querySelector("#fxview-tab-row-secondary-button").click();
                    return true;
                  }
                }
                return false;
                """,
                view_tag,
                row_tag,
                key,
                value,
            )
        )

    def _click_delete_in_menu(self, view_tag: str) -> bool:
        """Click the Delete item of the open row menu; False if no menu is open."""
        return bool(
            self.driver.execute_script(
                """
                const panel = document.querySelector(arguments[0])?.shadowRoot
                  ?.querySelector("panel-list");
                if (!panel || !panel.matches(":popover-open")) return false;
                const item = panel.querySelector("panel-item[data-l10n-id$='context-delete']");
                if (!item) return false;
                item.click();
                return true;
                """,
                view_tag,
            )
        )

    def _delete_row(self, view_tag: str, row_tag: str, key: str, value: str) -> None:
        self.wait.until(lambda _: self._open_row_menu(view_tag, row_tag, key, value))
        self.wait.until(lambda _: self._click_delete_in_menu(view_tag))

    def delete_history_entry(self, url: str) -> BasePage:
        """Open the entry's menu and choose Delete from History."""
        self._delete_row("view-history", "fxview-tab-row", "url", url)
        return self

    def delete_chat(self, conversation_id: str) -> BasePage:
        """Open the chat's menu and choose Delete from Chats."""
        self._delete_row("view-chats", "chats-tab-row", "id", conversation_id)
        return self

    def expect_history_url_gone(self, url: str) -> BasePage:
        """Wait until `url` is no longer listed in History."""
        self.wait.until(lambda _: url not in self.get_history_urls())
        return self

    def expect_chat_gone(self, conversation_id: str) -> BasePage:
        """Wait until the conversation is no longer listed in Chats."""
        self.wait.until(lambda _: conversation_id not in self.get_chat_ids())
        return self
