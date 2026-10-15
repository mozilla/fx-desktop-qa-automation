from modules.browser_object_smart_bar import SmartBar
from modules.browser_object_smart_window import CHAT_DOCUMENT_JS
from modules.page_base import BasePage

# MESSAGE_ROLE.USER in the conversation model.
USER_ROLE = 0

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
