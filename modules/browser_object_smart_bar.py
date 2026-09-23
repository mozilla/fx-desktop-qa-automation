import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from modules.browser_object_smart_window import SmartWindow
from modules.page_base import BasePage

# The Smart Bar lives in <browser id="ai-window-browser"> with the editor two
# shadow roots down, so the accessors below script the traversal. Both
# supported alternatives were tried and do not work here:
# switch_to_iframe_context() raises NoSuchFrameException (it is a XUL
# <browser>, not an iframe), and element.shadow_root is content-context only.
# components.json shadowParent is not JS-free either -- see util.py:834/877.
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
        button does not exist in a Classic Window. The click goes through
        SmartWindow, which owns the Ask button's selector.
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

        Real key events, not `MultilineEditor.value`: assigning the property
        skips the editor's input handling, which is why the @-mention popup
        shows "No results found" when driven that way.

        Focus has to be scripted -- elements inside the ai-window-browser
        contentDocument have no usable Selenium reference from chrome
        (send_keys on one raises StaleElementReferenceException), so there is
        nothing to click first.
        """
        logging.info("Setting Smart Bar text to %r", text)
        focused = self._script(
            "const p = prosemirror();if (!p) return false;p.focus();return true;"
        )
        if not focused:
            raise AssertionError("Smart Bar editor is not available to write to")

        with self.driver.context(self.driver.CONTEXT_CHROME):
            # Select-all so this replaces rather than appends.
            # perform_key_combo maps CONTROL to COMMAND on macOS.
            self.perform_key_combo(Keys.CONTROL, "a")
            self.actions.send_keys(text).perform()

        self.expect_smart_bar_text(text)
        return self

    def expect_smart_bar_text(self, text: str) -> BasePage:
        """
        Wait until the Smart Bar's text equals `text`.

        Reports the actual value on timeout: the comparison is exact, so a
        future serialisation change (a trailing newline, say) would otherwise
        give a bare TimeoutException with nothing to point at.
        """
        try:
            self.expect(lambda _: self.get_smart_bar_text() == text)
        except TimeoutException:
            raise AssertionError(
                f"Smart Bar text never became {text!r}; "
                f"last read {self.get_smart_bar_text()!r}"
            ) from None
        return self

    # ── Searching ────────────────────────────────────────────────────────

    def submit(self) -> BasePage:
        """
        Press Enter to run whatever action the Smart Bar is currently set to.

        Sent as a real key event: the CTA acts on keyboard input, and there is
        no addressable element to click from chrome.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.actions.send_keys(Keys.ENTER).perform()
        return self

    def choose_search_engine(self, engine_name: str) -> BasePage:
        """
        Pick an engine from the Search With submenu by its visible name.

        Only sets the engine -- call submit() to run the search. The choice is
        not reflected in any CTA attribute, so assert on the resulting URL.
        """
        logging.info("Choosing Smart Bar search engine %r", engine_name)
        result = self._script(
            "const lists = ctaLists();"
            "if (lists.length !== 2) return {count: lists.length};"
            "const items = Array.from(lists[1].querySelectorAll('panel-item'));"
            "const hit = items.find(i => (i.textContent || '').trim() === arguments[0]);"
            "if (!hit) return {available: items.map(i => (i.textContent || '').trim())};"
            "hit.click();"
            "return {clicked: true};",
            engine_name,
        )
        if "count" in result:
            raise AssertionError(
                f"expected 2 panel-lists in the CTA (actions, Search With), "
                f"found {result['count']}"
            )
        if "available" in result:
            raise AssertionError(
                f"no Search With entry named {engine_name!r}; "
                f"available: {result['available']}"
            )
        return self

    @BasePage.context_chrome
    def get_result_count(self) -> int:
        """
        Return how many autocomplete rows the Smart Bar is showing.

        The results live in the Smart Bar's urlbar view rather than the CTA,
        so this walks to `.urlbarView-results` instead of reusing ctaLists().
        """
        return self.driver.execute_script("""
            const br = document.getElementById("ai-window-browser");
            const doc = br && br.contentDocument;
            if (!doc) return 0;
            let rows = 0;
            (function walk(node, depth) {
                if (!node || depth > 12 || rows) return;
                for (const el of node.querySelectorAll("*")) {
                    if (el.matches && el.matches(".urlbarView-results")) {
                        rows = el.querySelectorAll(".urlbarView-row").length;
                        return;
                    }
                    if (el.shadowRoot) { walk(el.shadowRoot, depth + 1); if (rows) return; }
                }
            })(doc, 0);
            return rows;
        """)

    def expect_results(self, minimum: int = 1) -> BasePage:
        """Wait until the Smart Bar shows at least `minimum` autocomplete rows."""
        self.expect(lambda _: self.get_result_count() >= minimum)
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

        The split button's menu portion is not separately clickable, so this
        goes through the panel-list's own toggle() -- which flips state, hence
        the open check.
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

        Read as text because engine names carry no l10n ids, and read without
        expanding the submenu, which works because its items render eagerly.
        Returns an empty list if that ever changes.

        Raises if the CTA stops holding exactly two panel-lists, since the
        submenu is reached by position.
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
