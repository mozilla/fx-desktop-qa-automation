import re

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from .browser_object_smart_bar import SmartBar
from .browser_object_smart_window import CHAT_DOCUMENT_JS
from .page_base import BasePage

# MESSAGE_ROLE.USER and MESSAGE_ROLE.TOOL in the conversation model.
USER_ROLE = 0
TOOL_ROLE = 3

# uiTypes of the cards the assistant shows when it asks before grouping or
# closing tabs, and of the card that shows an action's result (it replaces
# the first once the user confirms).
TAB_GROUP_CONFIRMATION = "tab-group-confirmation"
TAB_CLOSE_CONFIRMATION = "website-confirmation"
TAB_ACTION_CONFIRMATIONS = (TAB_GROUP_CONFIRMATION, TAB_CLOSE_CONFIRMATION)
ACTION_RESULT = "ai-action-result"

# How the model names a tab in tool calls: §url_token: LOCALHOST_LASAGNA_HTML_1§
URL_TOKEN_RE = re.compile(r"§url_token:\s*([A-Z0-9_]+_\d+)§")

# Tool calls make a turn several LLM round trips; record and live modes wait
# on the real service for each.
TURN_TIMEOUT = 120


# The messages render in <browser id="aichat-browser">, a remote
# about:aichatcontent page: chrome JS can't read its DOM and Selenium can't
# switch to it. A one-off frame script runs the code there and posts the
# result back. Resolves to {value: null} if the chat page isn't there yet.
_RUN_IN_CHAT = r"""
const [body, args] = arguments;
const done = arguments[arguments.length - 1];
const aw = aiWindow();
const chat = aw && aw.shadowRoot &&
  aw.shadowRoot.querySelector("#aichat-browser");
if (!chat || !chat.messageManager) {
  done({ value: null });
  return;
}
const mm = chat.messageManager;
const name = "starfox:chat-script:" + Math.random();
mm.addMessageListener(name, function listener(msg) {
  mm.removeMessageListener(name, listener);
  done(msg.data);
});
const frameScript = `
  (async () => {
    try {
      const args = ${JSON.stringify(args)};
      const value = await (async () => { ${body} })();
      sendAsyncMessage(${JSON.stringify(name)}, { value });
    } catch (e) {
      sendAsyncMessage(${JSON.stringify(name)}, { error: String(e) });
    }
  })();
`;
mm.loadFrameScript(
  "data:application/javascript;charset=utf-8," + encodeURIComponent(frameScript),
  false
);
"""


# A reply's web sources are chips in its chat-assistant-citations row. Those
# that don't fit are grouped behind the row's "+n more" button, in a panel
# holding copies of their chips.
_SOURCES_JS = r"""
function sourcesRow() {
  const chat = content.document.querySelector("ai-chat-content");
  const rows = chat && chat.shadowRoot
    ? chat.shadowRoot.querySelectorAll("chat-assistant-citations") : [];
  return rows.length ? rows[rows.length - 1] : null;
}
function moreButton() {
  const row = sourcesRow();
  return row && row.shadowRoot.querySelector("moz-button.citations-more");
}
function morePanel() {
  const row = sourcesRow();
  const panel = row && row.shadowRoot.querySelector("smartwindow-panel-list");
  return panel && panel.shadowRoot;
}
function rowChips() {
  const row = sourcesRow();
  return row ? [...row.shadowRoot.querySelectorAll(".citations smartwindow-chip")]
    .filter(chip => !chip.closest("smartwindow-panel-list")) : [];
}
function panelChips() {
  const panel = morePanel();
  return panel ? [...panel.querySelectorAll("smartwindow-chip")] : [];
}
// Grouped chips stay in the row but are hidden with visibility, which a plain
// checkVisibility() doesn't count.
function shows(el) {
  return el.checkVisibility({ visibilityProperty: true, opacityProperty: true });
}
function chipLink(chip) {
  return chip.shadowRoot && chip.shadowRoot.querySelector("a.chip");
}
// Read from the chip's markup: the frame script can't see its JS properties.
function chipUrl(chip) {
  const link = chipLink(chip);
  return link ? link.getAttribute("href") : null;
}
function chipTitle(chip) {
  const label = chip.shadowRoot && chip.shadowRoot.querySelector(".chip-label");
  return label ? label.textContent.trim() : null;
}
function describe(chip) {
  const link = chipLink(chip);
  const icon = chip.shadowRoot && chip.shadowRoot.querySelector("img.chip-icon");
  return {
    title: chipTitle(chip),
    url: chipUrl(chip),
    grouped: !!(chip.parentElement && chip.parentElement.hasAttribute("data-overflow")),
    visible: !!link && shows(link),
    icon: !!icon && icon.complete && icon.naturalWidth > 0 && shows(icon),
  };
}
function findChip(url, inPanel) {
  return (inPanel ? panelChips() : rowChips()).find(chip => chipUrl(chip) === url);
}
// Mouse events synthesized in the chat page take the same path as a user's
// click, so Firefox picks where to open the link from the button.
function mouse(el, button) {
  const r = el.getBoundingClientRect();
  const x = r.left + r.width / 2, y = r.top + r.height / 2;
  const send = (type, buttons) => content.synthesizeMouseEvent
    ? content.synthesizeMouseEvent(type, x, y, { button, buttons, clickCount: 1 },
        { isDOMEventSynthesized: true })
    : content.windowUtils.sendMouseEvent(type, x, y, button, 1, 0);
  const pressed = [1, 4, 2][button];
  send("mousedown", pressed);
  if (button === 2) send("contextmenu", pressed);
  send("mouseup", 0);
}
"""

MOUSE_BUTTONS = {"left": 0, "middle": 1, "right": 2}


class SmartWindowChat(BasePage):
    """
    Browser Object Model for the Smart Window's AI chat conversation.

    Open the chat first (SmartBar.open_smart_bar() or open_full_page_chat()),
    then talk with send(), which returns once the assistant has answered.
    """

    URL_TEMPLATE = "about:blank"

    @BasePage.context_chrome
    def _ai_window_script(self, body: str, *args):
        return self.driver.execute_script(CHAT_DOCUMENT_JS + body, *args)

    @BasePage.context_chrome
    def _chat_script(self, body: str, *args):
        """
        Run `body`, the inside of an async function, in the chat page and
        return its result (None if the page hasn't loaded). There `content`
        is the page's window and `args` holds `args`.
        """
        result = self.driver.execute_async_script(
            CHAT_DOCUMENT_JS + _RUN_IN_CHAT, body, list(args)
        )
        if "error" in result:
            raise AssertionError(f"Script in the chat page failed: {result['error']}")
        return result["value"]

    # ── Sending ──────────────────────────────────────────────────────────

    def send(self, text: str) -> BasePage:
        """
        Send `text` from the Smart Bar and wait until the assistant has
        answered it, tool calls included.

        For a test that has to act while the assistant is still answering,
        use SmartBar.submit_chat() and expect_turn_complete() instead.
        """
        turn = self.get_sent_count() + 1
        SmartBar(self.driver).submit_chat(text)
        self.expect_turn_complete(turn)
        return self

    def send_typed(self) -> BasePage:
        """Send what's already in the Smart Bar, mentions included, and wait for the answer."""
        smart_bar = SmartBar(self.driver)
        if smart_bar.get_action() != "chat":
            raise AssertionError(
                f"The Smart Bar would {smart_bar.get_action()!r}, not send to chat"
            )
        turn = self.get_sent_count() + 1
        smart_bar.submit()
        # Firefox clears the Smart Bar once the message is sent; this fails fast if Enter was lost.
        smart_bar.expect_smart_bar_text("")
        self.expect_turn_complete(turn)
        return self

    def get_sent_count(self) -> int:
        """Return how many messages the user has sent in this conversation."""
        return self._ai_window_script(
            "const aw = aiWindow();"
            "const c = aw && aw.conversation;"
            "return c ? c.messages.filter(m => m.role === arguments[0]).length : 0;",
            USER_ROLE,
        )

    # ── Turn state ───────────────────────────────────────────────────────

    def is_turn_complete(self, turn: int = 1) -> bool:
        """
        Report whether `turn` messages have been sent and the assistant has
        finished answering the last, tool calls included. Counting messages
        keeps a follow-up's wait from passing on the earlier turn.
        """
        return bool(
            self._ai_window_script(
                "const aw = aiWindow();"
                "const c = aw && aw.conversation;"
                "return !!c && !aw.isGenerating &&"
                "  c.messages.filter(m => m.role === arguments[0]).length >= arguments[1];",
                USER_ROLE,
                turn,
            )
        )

    def expect_turn_complete(self, turn: int = 1) -> BasePage:
        """
        Wait until the assistant has finished answering message number
        `turn` of the conversation.
        """
        self.custom_wait(timeout=TURN_TIMEOUT).until(
            lambda _: self.is_turn_complete(turn),
            message=f"The assistant never finished turn {turn}",
        )
        return self

    # ── Messages ─────────────────────────────────────────────────────────

    def get_messages(self) -> list[dict]:
        """
        Return the messages shown in the chat, oldest first.

        Returns
        -------
        list[dict]
            Each with role ("user" or "assistant"), text, and complete (False
            while a reply is still streaming in).
        """
        return (
            self._chat_script("""
                const chat = content.document.querySelector("ai-chat-content");
                if (!chat || !chat.shadowRoot) return [];
                return [...chat.shadowRoot.querySelectorAll("ai-chat-message")]
                  .map(m => ({
                    role: m.dataset.messageRole,
                    text: (m.shadowRoot || m).textContent.replace(/\\s+/g, " ").trim(),
                    complete: m.hasAttribute("complete"),
                  }));
            """)
            or []
        )

    def get_last_reply(self) -> str | None:
        """Return the newest assistant message's text, or None if there is none."""
        replies = [m["text"] for m in self.get_messages() if m["role"] == "assistant"]
        return replies[-1] if replies else None

    # ── Tool actions ─────────────────────────────────────────────────────

    def get_tool_ui_types(self) -> list[str]:
        """
        Return the uiType of each tool result shown in the chat, oldest first,
        e.g. "tab-group-confirmation" for a card waiting on the user.
        """
        return self._ai_window_script(
            "const aw = aiWindow();"
            "const c = aw && aw.conversation;"
            "return c ? c.messages.filter(m => m.toolUIData)"
            "  .map(m => m.toolUIData.uiType) : [];"
        )

    def get_tool_results(self, name: str) -> list:
        """
        Return what Firefox sent back to the model for each call to tool
        `name`, oldest first.
        """
        return self._ai_window_script(
            "const aw = aiWindow();"
            "const c = aw && aw.conversation;"
            "return c ? c.messages"
            "  .filter(m => m.role === arguments[0] && m.content?.name === arguments[1])"
            "  .map(m => m.content.body) : [];",
            TOOL_ROLE,
            name,
        )

    def get_last_tool_ui_type(self) -> str | None:
        """Return the newest tool result's uiType, or None if there is none."""
        ui_types = self.get_tool_ui_types()
        return ui_types[-1] if ui_types else None

    def confirm_action(self) -> BasePage:
        """
        Click Confirm on the card the assistant is waiting on, and wait until
        Firefox has acted on it, which replaces the card with its result.
        """
        waiting = self.get_last_tool_ui_type()

        def _confirmed(_) -> bool:
            # Checked before each click, so a click that landed isn't repeated.
            if self.get_last_tool_ui_type() != waiting:
                return True
            # Retried, because a click that lands before the card is ready is
            # dropped.
            self._click_confirm()
            return False

        self.wait.until(
            _confirmed, message=f"Confirm on the {waiting} card never took effect"
        )
        return self

    def _click_confirm(self) -> bool:
        """Click the waiting card's Confirm button, if it's there yet."""
        return self._chat_script("""
            const chat = content.document.querySelector("ai-chat-content");
            const card = chat && chat.shadowRoot &&
              chat.shadowRoot.querySelector("ai-website-confirmation");
            const button = card && card.shadowRoot && card.shadowRoot
              .querySelector("moz-button[type='primary']:not([disabled])");
            if (!button) return false;
            button.click();
            return true;
        """)

    def undo_last_action(self) -> BasePage:
        """Click Undo on the newest action result card."""
        # Retried, because a click before the card is ready is dropped.
        self.wait.until(
            lambda _: self._click_undo(),
            message="The action result card never showed an Undo button",
        )
        return self

    def _click_undo(self) -> bool:
        """Click the newest Undo button on an action's result, if it's there yet."""
        # Undo can be on either card: after closing tabs it is on the confirmation card.
        return self._chat_script("""
            const hits = [];
            (function walk(node, depth) {
              if (!node || depth > 12) return;
              for (const el of node.querySelectorAll("*")) {
                if (el.matches("moz-button.action-confirmation-undo, moz-button.action-result-undo")) {
                  hits.push(el);
                }
                if (el.shadowRoot) walk(el.shadowRoot, depth + 1);
              }
            })(content.document, 0);
            const button = hits[hits.length - 1];
            if (!button) return false;
            button.click();
            return true;
        """)

    def confirm_tab_action_if_asked(self) -> BasePage:
        """
        Confirm the tab grouping or closing if the assistant asked first.
        Asking is the model's choice (manage_tabs' ask_confirmation), so a
        recording can take either path.
        """
        # The card can arrive just after the turn ends, so wait for it first.
        self.expect(
            lambda _: (
                self.get_last_tool_ui_type()
                in (*TAB_ACTION_CONFIRMATIONS, ACTION_RESULT)
            )
        )
        if self.get_last_tool_ui_type() in TAB_ACTION_CONFIRMATIONS:
            self.confirm_action()
        return self

    # ── Web sources ──────────────────────────────────────────────────────

    def _sources_script(self, body: str, *args):
        return self._chat_script(_SOURCES_JS + body, *args)

    def get_sources(self) -> list[dict]:
        """
        Return the newest reply's web sources, in the row's order.

        Returns
        -------
        list[dict]
            Each with title, url, grouped (behind "+n more" rather than in
            the row), visible, and icon (its icon has loaded and shows).
        """
        return self._sources_script("return rowChips().map(describe);") or []

    def expect_sources(self, count: int) -> BasePage:
        """Wait until the newest reply shows `count` web sources."""
        self.expect(lambda _: len(self.get_sources()) == count)
        return self

    def sources_follow_last_reply(self) -> bool:
        """Report whether the sources row comes after the newest reply's text."""
        return self._sources_script("""
            const row = sourcesRow();
            const chat = content.document.querySelector("ai-chat-content");
            const replies = [...chat.shadowRoot.querySelectorAll(
              "ai-chat-message[data-message-role='assistant']")];
            const reply = replies[replies.length - 1];
            return !!row && !!reply &&
              !!(reply.compareDocumentPosition(row) & Node.DOCUMENT_POSITION_FOLLOWING);
        """)

    def get_grouped_sources_label(self) -> str | None:
        """Return the "+n more" button's text, or None while it's hidden."""
        return self._sources_script("""
            const more = moreButton();
            if (!more || more.hasAttribute("data-overflow")) return null;
            // Fluent fills the text in a moment after the button appears.
            return more.textContent.trim();
        """)

    def open_grouped_sources(self) -> BasePage:
        """Click "+n more" and wait for the panel of grouped sources."""
        self._sources_script("mouse(moreButton(), 0);")
        self.expect(
            lambda _: (
                (panel := self.get_grouped_sources())
                and all(s["visible"] for s in panel)
            )
        )
        return self

    def get_grouped_sources(self) -> list[dict]:
        """Return the sources in the "+n more" panel, described as in get_sources()."""
        return self._sources_script("return panelChips().map(describe);") or []

    def click_source(
        self, url: str, button: str = "left", grouped: bool = False
    ) -> BasePage:
        """
        Click the source chip for `url` with `button` ("left", "middle" or
        "right"). Set `grouped` for a chip in the "+n more" panel.
        """
        clicked = self._sources_script(
            """
            const chip = findChip(args[0], args[2]);
            if (!chip) return false;
            mouse(chipLink(chip), args[1]);
            return true;
            """,
            url,
            MOUSE_BUTTONS[button],
            grouped,
        )
        if not clicked:
            raise AssertionError(f"No source chip for {url} (grouped={grouped})")
        return self

    def get_focused_source(self) -> str | None:
        """Return the URL of the source chip with keyboard focus, if one has it."""
        return self._sources_script("""
            let el = content.document.activeElement;
            while (el && el.shadowRoot && el.shadowRoot.activeElement) {
              el = el.shadowRoot.activeElement;
            }
            const host = el && el.getRootNode().host;
            return el && el.matches("a.chip") && host.localName === "smartwindow-chip"
              ? chipUrl(host) : null;
        """)

    def tab_to_source(self, max_stops: int = 15) -> str:
        """
        Press Shift+Tab from the Smart Bar until a source chip has focus, and
        return its URL. The sources come before the Smart Bar in tab order.
        """
        smart_bar = SmartBar(self.driver)
        if not smart_bar.focus_editor():
            raise AssertionError("Smart Bar editor is not available to focus")
        for _ in range(max_stops):
            self.perform_key_combo_chrome(Keys.SHIFT, Keys.TAB)
            try:
                return self.custom_wait(timeout=1, poll_frequency=0.1).until(
                    lambda _: self.get_focused_source()
                )
            except TimeoutException:
                continue
        raise AssertionError(f"Shift+Tab never reached a source in {max_stops} stops")

    def get_source_accessibles(self, grouped: bool = False) -> list[dict]:
        """
        Return the role and name assistive technology gets for each source
        link shown: the row's, or with `grouped` the "+n more" panel's. Starts
        the accessibility service in the chat page if it isn't running.
        """
        return self._sources_script(
            """
            const svc = Cc["@mozilla.org/accessibilityService;1"]
              .getService(Ci.nsIAccessibilityService);
            const links = (args[0] ? panelChips() : rowChips())
              .map(chipLink).filter(link => link && shows(link));
            // The tree is built a moment after the service starts.
            for (let i = 0; i < 50 && links.some(l => !svc.getAccessibleFor(l)); i++) {
              await new Promise(r => content.setTimeout(r, 100));
            }
            return links.map(link => {
              const acc = svc.getAccessibleFor(link);
              return acc ? { role: svc.getStringRole(acc.role), name: acc.name } : null;
            });
            """,
            grouped,
        )

    def get_grouped_sources_button_accessible(self) -> dict | None:
        """Return the role and name assistive technology gets for "+n more"."""
        return self._sources_script("""
            const svc = Cc["@mozilla.org/accessibilityService;1"]
              .getService(Ci.nsIAccessibilityService);
            const more = moreButton();
            const button = more && more.shadowRoot && more.shadowRoot.querySelector("button");
            if (!button) return null;
            for (let i = 0; i < 50 && !svc.getAccessibleFor(button); i++) {
              await new Promise(r => content.setTimeout(r, 100));
            }
            const acc = svc.getAccessibleFor(button);
            return acc ? { role: svc.getStringRole(acc.role), name: acc.name } : null;
        """)

    def is_forced_colors_active(self) -> bool:
        """Report whether the chat page is drawn with forced (high contrast) colors."""
        return self._chat_script(
            'return content.matchMedia("(forced-colors: active)").matches;'
        )

    def get_source_colors(self, grouped: bool = False) -> list[dict]:
        """
        Return each shown source chip's label color and the color behind it,
        the first opaque background up the tree.
        """
        return self._sources_script(
            """
            const opaque = c => c && c !== "transparent" && !/rgba\\(.*,\\s*0\\)$/.test(c);
            function background(el) {
              for (let n = el; n; n = n.parentElement || (n.getRootNode() && n.getRootNode().host)) {
                const c = content.getComputedStyle(n).backgroundColor;
                if (opaque(c)) return c;
              }
              return content.getComputedStyle(content.document.documentElement).backgroundColor;
            }
            return (args[0] ? panelChips() : rowChips())
              .map(chip => chip.shadowRoot.querySelector(".chip-label"))
              .filter(label => label && shows(label))
              .map(label => ({ color: content.getComputedStyle(label).color,
                               background: background(label) }));
            """,
            grouped,
        )

    # ── URL tokens ───────────────────────────────────────────────────────

    def get_url_tokens(self) -> dict[str, str]:
        """Return the conversation's URL tokens, each mapped to its URL."""
        return dict(
            self._ai_window_script(
                "const aw = aiWindow();"
                "return aw && aw.conversation ? [...aw.conversation.tokenToUrl] : [];"
            )
        )

    def resolve_url_tokens(self, items: list[str]) -> list[str]:
        """
        Turn the URL tokens a tool call names tabs by into their URLs. Items
        that aren't known tokens are returned as they are.
        """
        urls = self.get_url_tokens()
        resolved = []
        for item in items:
            match = URL_TOKEN_RE.search(item)
            resolved.append(urls.get(match.group(1), item) if match else item)
        return resolved
