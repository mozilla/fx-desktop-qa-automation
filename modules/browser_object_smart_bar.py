import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from modules.browser_object_smart_window import SmartWindow
from modules.page_base import BasePage

# The Smart Bar lives in <browser id="ai-window-browser"> with the editor two
# shadow roots down (ai-window -> moz-multiline-editor), so the accessors below
# script the traversal. The two supported alternatives were both tried first:
#
#   switch_to_iframe_context()  NoSuchFrameException -- it is a XUL <browser>
#                               ([object XULFrameElement]), not an iframe.
#   element.shadow_root         "Only supported in content context", and this
#                               UI exists only in chrome.
#
# Note the components.json shadowParent path is not JS-free either: it falls
# back to execute_script for shadowRoot.children (util.py:834) and, in chrome,
# matches by string-searching outerHTML (util.py:877).
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
  // aiWindow.html nests about four shadow roots deep to reach the CTA; 12 is
  // headroom against further nesting while still bounding a bad walk.
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
// The CTA is a split button: [0] is its actions menu, [1] the Search With
// submenu. These are positional because the lists carry no id or other stable
// attribute to select on. To stop a layout change from silently reading the
// wrong list, get_search_with_items checks the list count is still 2.
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
ACTION_MENU_GO_TO_SITE = "aiwindow-input-cta-menu-label-navigate"
ACTION_MENU_SEARCH_WITH_DEFAULT = "aiwindow-input-cta-menu-label-search"
ACTION_MENU_SEARCH_WITH = "aiwindow-input-cta-menu-label-search-with"


class SmartBar(BasePage):
    """
    Browser Object Model for the Smart Window's Smart Bar input.

    The Smart Bar is the Smart Window's urlbar, reimplemented as a ProseMirror
    editor. Open it with open_smart_bar(), then type into it with
    set_smart_bar_text().
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

        The click is delegated to SmartWindow, which owns the Ask button's
        selector -- declaring it here too would mean two manifests to update
        if the id ever changes.
        """
        SmartWindow(self.driver).click_on("smart-window-ask-button")
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
        """
        Return the Smart Bar's current text, or "" before it is available.

        Returning a value rather than throwing lets expect() poll this during
        the window where the editor has not finished loading.
        """
        return self._script("const e = editor(); return e ? e.value : '';")

    def set_smart_bar_text(self, text: str) -> BasePage:
        """
        Replace the Smart Bar's text by typing it.

        Types with real key events rather than assigning MultilineEditor.value,
        so the editor's own input handling actually runs -- assigning `value`
        skips it, which is how the @-mention popup ends up rendering with "No
        results found" when driven that way.

        Only the focus call is scripted, and that part is not avoidable:
        elements inside the ai-window-browser contentDocument have no usable
        Selenium reference from chrome, so send_keys against the editor raises
        StaleElementReferenceException ("not known in the current browsing
        context"). There is nothing to click or type into without first
        focusing it from privileged JS.
        """
        logging.info("Setting Smart Bar text to %r", text)
        focused = self._script(
            "const p = prosemirror();if (!p) return false;p.focus();return true;"
        )
        if not focused:
            raise AssertionError("Smart Bar editor is not available to write to")

        with self.driver.context(self.driver.CONTEXT_CHROME):
            # Select-all first so this replaces rather than appends.
            # perform_key_combo maps CONTROL to COMMAND on macOS, so this stays
            # correct on the Linux CI workers too.
            self.perform_key_combo(Keys.CONTROL, "a")
            self.actions.send_keys(text).perform()

        self.expect_smart_bar_text(text)
        return self

    def expect_smart_bar_text(self, text: str) -> BasePage:
        """
        Wait until the Smart Bar's text equals `text`.

        On timeout this reports what the editor actually held. The comparison
        is exact, so any future serialisation change -- a trailing newline
        being the obvious candidate -- would otherwise surface as a bare
        TimeoutException with nothing to point at. (No trailing newline is
        present today; `value` round-trips exactly.)
        """
        try:
            self.expect(lambda _: self.get_smart_bar_text() == text)
        except TimeoutException:
            raise AssertionError(
                f"Smart Bar text never became {text!r}; "
                f"last read {self.get_smart_bar_text()!r}"
            ) from None
        return self

    # ── Go / Ask action menu ─────────────────────────────────────────────

    def is_action_menu_open(self) -> bool:
        """Report whether the CTA's Go/Ask action menu is open."""
        return bool(self._script("const l = ctaLists()[0]; return !!(l && l.open);"))

    def expect_action_menu_open(self, is_open: bool = True) -> BasePage:
        """Wait until the Go/Ask action menu is (or is not) open."""
        self.expect(lambda _: self.is_action_menu_open() == is_open)
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
        found = self._script(
            "const l = ctaLists()[0];"
            "if (!l) return false;"
            "if (!l.open) l.toggle(new MouseEvent('click'));"
            "return true;"
        )
        if not found:
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

        Reads the items **without expanding the submenu**, which works because
        they render eagerly rather than on expand (verified over five
        consecutive runs). If that ever changes this returns an empty list, and
        the submenu has to be opened first.

        Raises if the CTA stops holding exactly two panel-lists: the submenu
        is reached by position, so a new list inserted ahead of it would
        otherwise return another menu's contents as though they were engines.
        """
        # Count and read in one script so the shadow tree is only walked once.
        result = self._script(
            "const lists = ctaLists();"
            "if (lists.length !== 2) return {count: lists.length};"
            "return {items: Array.from(lists[1].querySelectorAll('panel-item'))"
            "  .map(i => (i.textContent || '').trim()).filter(t => t)};"
        )
        if "items" not in result:
            raise AssertionError(
                f"expected 2 panel-lists in the CTA (actions, Search With), "
                f"found {result['count']} -- the positional lookup in "
                f"ctaLists() is no longer safe and needs revisiting"
            )
        return result["items"]
