import logging

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
// Walk from the document: input-cta is not inside ai-window's own shadow
// root, so starting the search there misses it entirely.
function cta() {
  const d = aiDoc();
  if (!d) return null;
  let hit = null;
  (function walk(node, depth) {
    if (!node || depth > 12 || hit) return;
    for (const el of node.querySelectorAll("*")) {
      // Match with CSS, not tagName: these are HTML-namespaced elements in a
      // XUL document, so tagName reads back as "html:input-cta".
      if (el.matches && el.matches("input-cta")) { hit = el; return; }
      if (el.shadowRoot) { walk(el.shadowRoot, depth + 1); if (hit) return; }
    }
  })(d, 0);
  return hit;
}
// The CTA is a split button: [0] is its actions menu, [1] the Search With submenu.
function ctaLists() {
  const c = cta();
  return c && c.shadowRoot ? Array.from(c.shadowRoot.querySelectorAll("panel-list")) : [];
}
function menuItemIds(list) {
  return list
    ? Array.from(list.querySelectorAll("panel-item"))
        .map(i => i.getAttribute("data-l10n-id"))
        .filter(Boolean)
    : [];
}
"""

# panel-item data-l10n-ids in the CTA's actions menu. Matching on l10n id
# rather than visible text keeps these locale-independent.
ACTION_MENU_ASK = "aiwindow-input-cta-menu-label-chat"
ACTION_MENU_GO_TO_SITE = "aiwindow-input-cta-menu-label-navigate"
ACTION_MENU_SEARCH_WITH_DEFAULT = "aiwindow-input-cta-menu-label-search"
ACTION_MENU_SEARCH_WITH = "aiwindow-input-cta-menu-label-search-with"


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

    # ── Go / Ask action menu ─────────────────────────────────────────────

    def action_menu_open(self) -> bool:
        """Report whether the CTA's Go/Ask action menu is open."""
        return bool(self._script("const l = ctaLists()[0]; return !!(l && l.open);"))

    def expect_action_menu_open(self, is_open: bool = True) -> BasePage:
        """Wait until the Go/Ask action menu is (or is not) open."""
        self.expect(lambda _: self.action_menu_open() == is_open)
        return self

    def open_action_menu(self) -> BasePage:
        """
        Open the CTA's Go/Ask action menu, leaving it open if already shown.

        The CTA is a moz-button with type="split"; its menu portion is not a
        separate element that can be clicked directly, so the panel-list is
        opened through its own toggle(), which is the same entry point the
        split button uses. toggle() flips state, so an already-open menu is
        left alone rather than being closed.
        """
        opened = self._script(
            "const l = ctaLists()[0];"
            "if (!l) return false;"
            "if (!l.open) l.toggle(new MouseEvent('click'));"
            "return true;"
        )
        if not opened:
            raise AssertionError("CTA action menu not found")
        self.expect_action_menu_open(True)
        return self

    def get_action_menu_items(self) -> list[str]:
        """Return the action menu's panel-item data-l10n-ids, in order."""
        return self._script("return menuItemIds(ctaLists()[0]);")

    def get_search_with_items(self) -> list[str]:
        """
        Return the Search With submenu's entries as visible text, in order.

        Engine names are not localised strings with l10n ids, so these are
        read as text.
        """
        return self._script(
            "const l = ctaLists()[1];"
            "return l ? Array.from(l.querySelectorAll('panel-item'))"
            "  .map(i => (i.textContent || '').trim()).filter(t => t) : [];"
        )

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
