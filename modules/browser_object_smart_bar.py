import logging

from selenium.webdriver.common.keys import Keys

from modules.page_base import BasePage

# The Smart Bar renders inside <browser id="ai-window-browser">, whose document
# is chrome://browser/content/aiwindow/aiWindow.html, and the editor sits two
# shadow roots down (ai-window -> moz-multiline-editor). Neither a <browser>
# contentDocument nor that shadow chain is reachable through the components.json
# selector system, so the accessors below script the traversal instead. Each
# script is a single traversal or a single property read/write on the product's
# own MultilineEditor API.
_TRAVERSE = """
function aiDoc() {
  const b = document.getElementById("ai-window-browser");
  return b && b.contentDocument;
}
function editor() {
  const d = aiDoc();
  const host = d && d.querySelector("ai-window");
  return host && host.shadowRoot
    ? host.shadowRoot.querySelector("moz-multiline-editor")
    : null;
}
function prosemirror() {
  const e = editor();
  return e && e.shadowRoot ? e.shadowRoot.querySelector("div.ProseMirror") : null;
}
function inlineChips() {
  const p = prosemirror();
  return p ? Array.from(p.querySelectorAll("ai-website-chip")) : [];
}
"""


class SmartBar(BasePage):
    """
    Browser Object Model for the Smart Window's Smart Bar input.

    The Smart Bar is the Smart Window's urlbar, reimplemented as a ProseMirror
    editor. Open it with open_smart_bar(), then read/write text through the
    editor's own value API.
    """

    URL_TEMPLATE = "about:blank"

    @BasePage.context_chrome
    def _script(self, body: str, *args):
        return self.driver.execute_script(_TRAVERSE + body, *args)

    # ── Opening ──────────────────────────────────────────────────────────

    def open_smart_bar(self) -> BasePage:
        """
        Click the Ask button and wait for the Smart Bar editor to be ready.

        Requires the window to already be in the Smart Window state; the
        button does not exist in a Classic Window.
        """
        self.click_on("smart-window-ask-button")
        self.expect_smart_bar_ready()
        return self

    def smart_bar_ready(self) -> bool:
        """Report whether the Smart Bar editor exists and has finished loading."""
        return bool(
            self._script(
                "const d = aiDoc();"
                "return !!(d && d.readyState === 'complete' && editor());"
            )
        )

    def expect_smart_bar_ready(self) -> BasePage:
        """Wait until the Smart Bar editor is available."""
        self.expect(lambda _: self.smart_bar_ready())
        return self

    # ── Text ─────────────────────────────────────────────────────────────

    def get_smart_bar_text(self) -> str:
        """Return the Smart Bar's current text."""
        return self._script("return editor().value;")

    def set_smart_bar_text(self, text: str) -> BasePage:
        """
        Replace the Smart Bar's text.

        Assigns MultilineEditor.value, the element's own API, which replaces
        the full contents and keeps the ProseMirror document valid. Passing ""
        clears the field.
        """
        logging.info("Setting Smart Bar text to %r", text)
        self._script("editor().value = arguments[0];", text)
        self.expect_smart_bar_text(text)
        return self

    def clear_smart_bar(self) -> BasePage:
        """Clear the Smart Bar."""
        return self.set_smart_bar_text("")

    def expect_smart_bar_text(self, text: str) -> BasePage:
        """Wait until the Smart Bar's text equals `text`."""
        self.expect(lambda _: self.get_smart_bar_text() == text)
        return self

    # ── Tagging open tabs (@-mention) ────────────────────────────────────

    def _focus_editor(self) -> None:
        # _script is already chrome-scoped.
        self._script("prosemirror().focus();")

    @BasePage.context_chrome
    def tag_tab_via_mention(self, filter_text: str = "") -> BasePage:
        """
        Tag an open tab by typing "@" and accepting the first suggestion.

        Must use real keystrokes: assigning MultilineEditor.value renders the
        mention popup but never runs the tab query, so it returns "No results
        found". Only genuine input events trigger the lookup.

        Arguments:
            filter_text: typed after "@" to narrow the suggestions. Without it
                         the first tab in the list is taken.
        """
        before = len(self.get_tagged_sites())
        self._focus_editor()
        self.actions.send_keys(f"@{filter_text}").perform()
        self.actions.send_keys(Keys.ARROW_DOWN).perform()
        self.actions.send_keys(Keys.ENTER).perform()
        self.expect(lambda _: len(self.get_tagged_sites()) == before + 1)
        return self

    def get_tagged_sites(self) -> list[dict]:
        """
        Return the inline tagged sites as [{"label": ..., "href": ...}], in
        document order.
        """
        return self._script(
            "return inlineChips().map(c => ({label: c.label, href: c.href}));"
        )

    @BasePage.context_chrome
    def delete_last_tag(self) -> BasePage:
        """
        Remove the last inline tag with the backspace key.

        Sends backspace until the tag count actually drops: the first press
        consumes the trailing space the editor inserts after a mention, and
        only the second removes the chip.
        """
        before = len(self.get_tagged_sites())
        if not before:
            raise ValueError("no tagged sites to delete")
        self._focus_editor()
        # Two presses are expected (space, then chip); 4 gives safety headroom.
        for _ in range(4):
            self.actions.send_keys(Keys.BACKSPACE).perform()
            if len(self.get_tagged_sites()) < before:
                return self
        raise AssertionError(f"backspace did not remove a tag (still {before})")

    def expect_tagged_sites(self, count: int) -> BasePage:
        """Wait until exactly `count` sites are tagged inline."""
        self.expect(lambda _: len(self.get_tagged_sites()) == count)
        return self

    # ── Placeholder hints ────────────────────────────────────────────────

    def get_placeholder_hints(self) -> list[str]:
        """
        Return the rotating placeholder hints shown while the Smart Bar is
        empty. Empty list once the field has text.
        """
        return self._script(
            "const p = prosemirror();"
            "return p ? Array.from(p.querySelectorAll('.placeholder-hints li'))"
            "  .map(li => li.textContent.trim()) : [];"
        )
