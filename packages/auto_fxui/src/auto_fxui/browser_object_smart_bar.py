import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from .browser_object_smart_window import CHAT_DOCUMENT_JS, SmartWindow
from .browser_object_tabbar import TabBar
from .page_base import BasePage

# The Smart Bar lives in the chat's document (see CHAT_DOCUMENT_JS) with the
# editor two shadow roots down, so the accessors below script the traversal.
# Both supported alternatives were tried and do not work here:
# switch_to_iframe_context() raises NoSuchFrameException (it is a XUL
# <browser>, not an iframe), and element.shadow_root is content-context only.
# components.json shadowParent is not JS-free either -- see util.py:834/877.
_TRAVERSE = (
    CHAT_DOCUMENT_JS
    + """
function editor() {
  const host = aiWindow();
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
// The autocomplete rows live in the Smart Bar's urlbar view, not the CTA.
function resultsView() {
  return deepAll(".urlbarView-results")[0] || null;
}
// Every element in the chat document matching `sel`, through all shadow roots.
function deepAll(sel) {
  const hits = [];
  (function walk(node, depth) {
    if (!node || depth > 14) return;
    for (const el of node.querySelectorAll("*")) {
      if (el.matches && el.matches(sel)) hits.push(el);
      if (el.shadowRoot) walk(el.shadowRoot, depth + 1);
    }
  })(aiDoc(), 0);
  return hits;
}
function modelSelect() {
  return deepAll("input-model-select")[0] || null;
}
function modelMenu() {
  const m = modelSelect();
  return m && m.shadowRoot ? m.shadowRoot.querySelector("panel-list") : null;
}
// The open "@" mentions panel; the same component also lists "/" commands.
function mentionsPanel() {
  return deepAll("smartwindow-panel-list").find(p => {
    const l = p.shadowRoot && p.shadowRoot.querySelector("panel-list");
    return l && l.open;
  }) || null;
}
// The focused element, followed into shadow roots: [host, ..., innermost].
function focusChain() {
  const chain = [];
  let el = aiDoc() && aiDoc().activeElement;
  while (el) {
    chain.push(el);
    el = el.shadowRoot && el.shadowRoot.activeElement;
  }
  return chain;
}
"""
)

# The Smart Bar's buttons in Tab order, each as (host class, inner button id).
# The inner id tells the Ask/Go button from the arrow that opens its menu.
SMART_BAR_BUTTONS = {
    "context": ("context-icon-button", "main-button"),
    "memories": ("memories-icon-button", "main-button"),
    "model": ("input-model-select-button", "main-button"),
    "cta": ("input-cta", "main-button"),
    "cta-menu": ("input-cta", "chevron-button"),
}

# UrlbarResult providers behind the Smart Bar's rows.
PROVIDER_AI_CHAT = "UrlbarProviderAiChat"
PROVIDER_SEARCH_SUGGESTIONS = "UrlbarProviderSearchSuggestions"

# panel-item data-l10n-ids in the CTA's actions menu. Matching on l10n id
# rather than visible text keeps these locale-independent.
ACTION_MENU_CHAT = "aiwindow-input-cta-menu-label-chat"
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
        Click the Ask button and wait for the editor to be ready.

        Requires an active Smart Window; the button does not exist otherwise.
        """
        SmartWindow(self.driver).click_on("smart-window-ask-button")
        self.expect_smart_bar_ready()
        return self

    def open_full_page_chat(self) -> BasePage:
        """
        Open a new tab, which in a Smart Window is the full-page chat, and
        wait for its Smart Bar.
        """
        TabBar(self.driver).new_tab_by_button()
        self.expect_smart_bar_ready()
        return self

    def click_footer_button(self, l10n_id: str) -> BasePage:
        """
        Click a Home page footer button, e.g. "smartwindow-footer-history".

        Scripted like the rest of this BOM: the footer lives in the chat
        document, which has no Selenium handle from chrome.
        """
        clicked = self._script(
            """
            const doc = aiDoc();
            // Bind before the walk: inside it, `arguments` is walk's own.
            const wanted = arguments[0];
            let hit = null;
            (function walk(node, depth) {
                if (!node || depth > 12 || hit) return;
                for (const el of node.querySelectorAll("*")) {
                    if (el.getAttribute("data-l10n-id") === wanted) {
                        hit = el; return;
                    }
                    if (el.shadowRoot) { walk(el.shadowRoot, depth + 1); if (hit) return; }
                }
            })(doc, 0);
            if (!hit) return false;
            hit.click();
            return true;
            """,
            l10n_id,
        )
        if not clicked:
            raise AssertionError(f"No Home page footer button {l10n_id!r}")
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

    def _focus_editor(self) -> bool:
        """
        Focus the ProseMirror editor; False if it is not available.

        Scripted: elements in the ai-window-browser contentDocument have no
        usable Selenium reference from chrome, so there is nothing to click.
        """
        return bool(
            self._script(
                "const p = prosemirror();if (!p) return false;p.focus();return true;"
            )
        )

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

        Real key events, not `MultilineEditor.value`: assigning that property
        skips the editor's input handling.
        """
        logging.info("Setting Smart Bar text to %r", text)
        if not self._focus_editor():
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

        Reports the value seen on timeout, since the comparison is exact.
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
        Press Enter to run the Smart Bar's current action.

        Refocuses first: send_keys goes to whatever holds focus, and
        choose_search_engine can move it.
        """
        if not self._focus_editor():
            raise AssertionError("Smart Bar editor is not available to submit from")
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.actions.send_keys(Keys.ENTER).perform()
        return self

    def get_default_search_engine(self) -> str:
        """
        Return the engine the CTA names as default, or "" if not shown yet.

        Read from the "Search with X" item's data-l10n-args, so a test need
        not hardcode an engine.
        """
        return self._script(
            "const l = ctaLists()[0];"
            "if (!l) return '';"
            "const hit = Array.from(l.querySelectorAll('panel-item'))"
            "  .find(i => i.getAttribute('data-l10n-id') === arguments[0]);"
            "if (!hit) return '';"
            "try {"
            "  return JSON.parse(hit.getAttribute('data-l10n-args') || '{}')"
            "    .searchEngineName || '';"
            "} catch (e) { return ''; }",
            ACTION_MENU_SEARCH_WITH_DEFAULT,
        )

    def expect_default_search_engine(self) -> BasePage:
        """Wait until the CTA reports which engine is the default."""
        try:
            self.expect(lambda _: self.get_default_search_engine() != "")
        except TimeoutException:
            raise AssertionError(
                "the CTA never named a default search engine"
            ) from None
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

    def expect_search_engine_offered(self, engine_name: str) -> BasePage:
        """
        Wait until `engine_name` appears in the Search With submenu.

        A count would be satisfied before this engine is added.
        """
        try:
            self.expect(lambda _: engine_name in (self._read_search_with_items() or []))
        except TimeoutException:
            raise AssertionError(
                f"{engine_name} never appeared in the Search With submenu; "
                f"last saw {self._read_search_with_items()}"
            ) from None
        return self

    def expect_search_engines(self, minimum: int = 2) -> BasePage:
        """
        Wait until the Search With submenu lists at least `minimum` entries.

        It holds only a generic "Search" entry until the search service
        initialises, so reading it immediately is a race.
        """
        try:
            self.expect(lambda _: len(self._read_search_with_items() or []) >= minimum)
        except TimeoutException:
            raise AssertionError(
                f"Search With submenu never listed {minimum} entries; "
                f"last saw {self._read_search_with_items()}"
            ) from None
        return self

    def get_result_count(self) -> int:
        """Return how many autocomplete rows the Smart Bar is showing."""
        return self._script("""
            const view = resultsView();
            return view ? view.querySelectorAll(".urlbarView-row").length : 0;
        """)

    def get_results(self) -> list[dict]:
        """
        Return the Smart Bar's autocomplete rows, top first.

        Returns
        -------
        list[dict]
            Each with provider, heuristic, text (the suggestion or title) and
            label (the row's visible action, e.g. "Ask").
        """
        return self._script("""
            const view = resultsView();
            if (!view) return [];
            return Array.from(view.querySelectorAll(".urlbarView-row"), row => ({
              provider: row.result?.providerName ?? null,
              heuristic: !!row.result?.heuristic,
              text: row.result?.payload.suggestion ?? row.result?.payload.title ?? "",
              label: row.querySelector(".urlbarView-action")?.textContent.trim() ?? "",
            }));
        """)

    def expect_results_from(self, *providers: str) -> BasePage:
        """Wait until every one of `providers` has a row in the Smart Bar."""

        def _shown() -> set[str]:
            return {r["provider"] for r in self.get_results()}

        try:
            self.expect(lambda _: set(providers) <= _shown())
        except TimeoutException:
            raise AssertionError(
                f"Expected rows from {providers}; rows were {self.get_results()}"
            ) from None
        return self

    def expect_no_results(self) -> BasePage:
        """
        Wait until the Smart Bar shows no autocomplete rows.

        Separate from expect_results, which waits for *at least* a count and
        so is trivially true at zero.
        """
        try:
            self.expect(lambda _: self.get_result_count() == 0)
        except TimeoutException:
            raise AssertionError(
                f"Smart Bar still showed {self.get_result_count()} autocomplete "
                "row(s) before any input"
            ) from None
        return self

    def expect_results(self, minimum: int = 1) -> BasePage:
        """
        Wait until the Smart Bar shows at least `minimum` autocomplete rows.

        Reports the count actually reached, matching expect_smart_bar_text.
        """
        try:
            self.expect(lambda _: self.get_result_count() >= minimum)
        except TimeoutException:
            raise AssertionError(
                f"Smart Bar never reached {minimum} autocomplete row(s); "
                f"last count {self.get_result_count()}"
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

        The split button's menu portion is not separately clickable, so this
        uses the panel-list's own toggle() -- which flips, hence the check.
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

    def _read_search_with_items(self) -> list[str] | None:
        """
        Search With entries, or None while the CTA has the wrong list count.

        None rather than raising, so a poll can wait the CTA out.
        """
        # Count and read in one script so the shadow tree is only walked once.
        result = self._script(
            "const lists = ctaLists();"
            "if (lists.length !== 2) return {count: lists.length};"
            "return {items: Array.from(lists[1].querySelectorAll('panel-item'))"
            "  .map(i => (i.textContent || '').trim()).filter(t => t)};"
        )
        return result.get("items")

    def get_search_with_items(self) -> list[str]:
        """
        Search With entries as visible text, in order. Raises if the CTA
        stops holding the two panel-lists the lookup relies on.
        """
        items = self._read_search_with_items()
        if items is None:
            raise AssertionError(
                "expected 2 panel-lists in the CTA (actions, Search With) -- "
                "the positional lookup in ctaLists() is no longer safe"
            )
        return items

    # ── Submitting ───────────────────────────────────────────────────────

    def get_action(self) -> str:
        """Return the CTA's current action: "chat", "search", "navigate" or ""."""
        return self._script("const c = cta(); return c ? c.action : '';")

    def choose_chat_action(self) -> BasePage:
        """
        Pick Ask (chat) from the Go/Ask action menu, leaving the menu closed.

        A scripted click on the item doesn't close the menu the way a real
        one does, so it is hidden explicitly.
        """
        self.open_action_menu()
        found = self._script(
            "const l = ctaLists()[0];"
            "const item = l && l.querySelector(`panel-item[data-l10n-id='${arguments[0]}']`);"
            "if (!item) return false;"
            "item.click();"
            "if (l.open) l.hide();"
            "return true;",
            ACTION_MENU_CHAT,
        )
        if not found:
            raise AssertionError("Chat item not found in the CTA action menu")
        self.expect(lambda _: self.get_action() == "chat")
        self.expect_action_menu_open(False)
        return self

    def submit_chat(self, text: str) -> BasePage:
        """
        Type `text` and send it to the assistant as a chat message.
        """
        self.set_smart_bar_text(text)
        self.choose_chat_action()
        clicked = self._script(
            "const b = cta().shadowRoot.querySelector('moz-button');"
            "if (!b || !b.buttonEl) return false;"
            "b.buttonEl.click();"
            "return true;"
        )
        if not clicked:
            raise AssertionError("Smart Bar CTA button not found")
        # Firefox clears the Smart Bar once the message is sent.
        self.expect_smart_bar_text("")
        return self

    # ── @ mentions ───────────────────────────────────────────────────────

    def type_mention_trigger(self) -> BasePage:
        """Type "@" at the end of the Smart Bar's text, which opens the mentions panel."""
        if not self._focus_editor():
            raise AssertionError("Smart Bar editor is not available to write to")
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.actions.send_keys(Keys.END).send_keys("@").perform()
        self.expect(lambda _: self._script("return !!mentionsPanel();"))
        return self

    def get_mention_suggestions(self) -> list[dict]:
        """Return the open mentions panel's items, each with id (the tab URL) and title."""
        return self._script("""
            const p = mentionsPanel();
            if (!p) return [];
            return (p.groups || []).flatMap(g => (g.items || []).map(i => ({
              id: i.id, title: i.label || i.title || "",
            })));
        """)

    def choose_mention(self, tab_url: str) -> BasePage:
        """Click the mentions panel's item for the tab showing `tab_url`."""
        clicked = self._script(
            "const p = mentionsPanel();"
            "if (!p) return false;"
            "const item = Array.from(p.shadowRoot.querySelectorAll('panel-item'))"
            "  .find(i => i.itemId === arguments[0]);"
            "if (!item) return false;"
            "item.click();"
            "return true;",
            tab_url,
        )
        if not clicked:
            raise AssertionError(
                f"{tab_url} not in the mentions panel: {self.get_mention_suggestions()}"
            )
        self.expect(lambda _: not self._script("return !!mentionsPanel();"))
        return self

    def get_inline_mentions(self) -> list[str]:
        """Return the labels of the mention chips inside the Smart Bar's text."""
        return self._script(
            "const p = prosemirror();"
            "return p ? Array.from(p.querySelectorAll('smartwindow-chip.mention'),"
            "  c => c.label || '') : [];"
        )

    # ── AI model picker ──────────────────────────────────────────────────

    def get_models(self) -> dict[str, str]:
        """
        Return the models the picker offers, by brand name, once they have loaded.

        Returns
        -------
        dict[str, str]
            Brand name (e.g. "Qwen") to the model id Firefox sends in requests.
        """
        self.expect_models_loaded()
        return self._read_models()

    def expect_models_loaded(self) -> BasePage:
        """Wait until the picker has its model list and a selected model."""
        # Firefox loads the list in the background after the Smart Bar is ready.
        try:
            self.expect(lambda _: self._read_models() and self.get_selected_model())
        except TimeoutException:
            raise AssertionError(
                f"The model picker never loaded: models {self._read_models()}, "
                f"selected {self.get_selected_model()!r}"
            ) from None
        return self

    def _read_models(self) -> dict[str, str]:
        return self._script(
            "const m = modelSelect();"
            "if (!m || !m.availableModels) return {};"
            "return Object.fromEntries(Object.values(m.availableModels)"
            "  .map(v => [v.brandName, v.model]));"
        )

    def get_selected_model(self) -> str:
        """Return the model id the picker shows as selected."""
        return self._script(
            "const m = modelSelect(); return m ? m.selectedModelId : '';"
        )

    def is_model_menu_open(self) -> bool:
        """Report whether the model picker's menu is open."""
        return bool(self._script("const l = modelMenu(); return !!(l && l.open);"))

    def model_menu_has_focus(self) -> bool:
        """Report whether keyboard focus is on an item in the open model menu."""
        return bool(
            self._script(
                "return focusChain().some(e => e.classList &&"
                "  e.classList.contains('model-item'));"
            )
        )

    def open_model_menu(self) -> BasePage:
        """Click the model picker and wait for its menu."""
        clicked = self._script(
            "const m = modelSelect();"
            "const b = m && m.shadowRoot && m.shadowRoot.querySelector('.input-model-select-button');"
            "const l = modelMenu();"
            "if (!b || !l) return false;"
            "if (!l.open) b.click();"
            "return true;"
        )
        if not clicked:
            raise AssertionError("Smart Bar model picker not found")
        self.expect(lambda _: self.is_model_menu_open())
        return self

    def get_model_menu_items(self) -> list[str]:
        """Return the labels of the models listed in the open model menu."""
        return self._script(
            "const l = modelMenu();"
            "return l ? Array.from(l.querySelectorAll('.model-item'),"
            "  b => b.querySelector('.model-item-label').textContent.trim()) : [];"
        )

    def choose_model(self, brand_name: str) -> BasePage:
        """Pick the `brand_name` model from the model menu."""
        model_id = self.get_models().get(brand_name)
        if not model_id:
            raise AssertionError(f"No {brand_name} model offered: {self.get_models()}")
        self.open_model_menu()
        # The menu doesn't keep availableModels' order, so match the label.
        clicked = self._script(
            "const m = modelSelect();"
            "const info = Object.values(m.availableModels).find(v => v.model === arguments[0]);"
            "const item = Array.from(modelMenu().querySelectorAll('.model-item')).find(b =>"
            "  b.querySelector('.model-item-label').textContent.trim() === info.shortName);"
            "if (!item) return false;"
            "item.click();"
            "return true;",
            model_id,
        )
        if not clicked:
            raise AssertionError(f"{brand_name} is not in the model menu")
        self.expect(
            lambda _: self.get_selected_model() == model_id
            and not self.is_model_menu_open()
        )
        return self

    # ── Keyboard ─────────────────────────────────────────────────────────

    def get_focused_button(self) -> str | None:
        """Return which of SMART_BAR_BUTTONS has keyboard focus, or None."""
        return self._script(
            "const chain = focusChain();"
            "for (const [name, [hostClass, innerId]] of Object.entries(arguments[0])) {"
            "  if (chain.some(e => e.classList && e.classList.contains(hostClass))"
            "      && chain.some(e => e.id === innerId)) return name;"
            "}"
            "return null;",
            SMART_BAR_BUTTONS,
        )

    def is_editor_focused(self) -> bool:
        """Report whether the Smart Bar's text field has keyboard focus."""
        # A document keeps its activeElement while the window's focus is elsewhere.
        return bool(
            self._script(
                "const doc = aiDoc();"
                "const host = doc && doc.defaultView && doc.defaultView.docShell"
                "  && doc.defaultView.docShell.chromeEventHandler;"
                "return document.activeElement === host"
                "  && focusChain().some(e => e === prosemirror());"
            )
        )

    def tab_to_button(self, name: str, max_stops: int = 15) -> BasePage:
        """Press Tab from the text field until button `name` has focus."""
        if not self._focus_editor():
            raise AssertionError("Smart Bar editor is not available to focus")
        # More stops than buttons: with suggestions showing, Tab steps through them first.
        for _ in range(max_stops):
            before = self.get_focused_button()
            self.perform_key_combo_chrome(Keys.TAB)
            # Focus moves a moment after the key, so wait briefly for it to
            # change; inside the suggestions it stays on the text field.
            try:
                self.custom_wait(timeout=1, poll_frequency=0.1).until(
                    lambda _: self.get_focused_button() != before
                )
            except TimeoutException:
                pass
            if self.get_focused_button() == name:
                return self
        raise AssertionError(
            f"Tab never reached the {name} button in {max_stops} stops"
        )

    def choose_action_with_keyboard(self, l10n_id: str) -> BasePage:
        """
        Open the Go/Ask menu with Enter and pick item `l10n_id` with the arrow keys.
        """
        self.tab_to_button("cta-menu")
        self.perform_key_combo_chrome(Keys.ENTER)
        self.expect_action_menu_open(True)
        items = self.get_action_menu_items()
        if l10n_id not in items:
            raise AssertionError(f"{l10n_id} not in the action menu: {items}")

        def _focused(_) -> bool:
            return self._script(
                "return focusChain().some(e => e.getAttribute &&"
                "  e.getAttribute('data-l10n-id') === arguments[0]);",
                l10n_id,
            )

        # Where focus starts isn't fixed, and it moves a moment after each key.
        for _ in range(len(items) + 1):
            try:
                self.custom_wait(timeout=1).until(_focused)
                break
            except TimeoutException:
                self.perform_key_combo_chrome(Keys.ARROW_DOWN)
        else:
            raise AssertionError(f"The arrow keys never reached {l10n_id}")
        self.perform_key_combo_chrome(Keys.ENTER)
        self.expect_action_menu_open(False)
        return self
