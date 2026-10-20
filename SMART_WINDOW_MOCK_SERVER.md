# Smart Window Mock Server

Smart Window chat tests never talk to the real LLM service (MLPA). Firefox sends its chat
and web search requests to a local mock server, which answers with responses recorded
earlier. Tests get the same replies on every run, need no account, and take seconds.

```
test → BOMs (SmartBar, SmartWindowChat) → Firefox
Firefox ──(endpoint prefs)──► MockServer ──► replay: data/recordings/... JSON
                                       └──► record / live: stage MLPA, with your token
```

Everything Firefox does with a reply is still real: running tools, showing cards, grouping
tabs, rendering. Only the model's replies come from the recording.

## Get started

Run the existing chat tests. No token or setup is needed:

```bash
pytest tests/smart_window/test_c3374375_continue_conversation_in_sidebar.py
```

pytest starts the mock server itself (the `mock_server_session` fixture), one per parallel
worker on a random port, and stops it at the end. There is nothing to start by hand, in CI or
locally.

## Modes

`--mock-mode` picks how the mock server answers. Leave it out and you get `replay`.

| Mode | What it does | Use it for |
|---|---|---|
| `replay` (default) | Serves the test's recording | Everyday runs, the pre-commit hook, CI |
| `record` | Forwards to stage MLPA and saves the responses as the recording | A new chat test, or when replay asks you to |
| `live` | Forwards to stage MLPA without saving | Checking that a recording still matches the real service |

Only tests that use the mock server read the flag. Every other test ignores it.

## Write a chat test

1. **Pick the TestRail case and the chat.** Use the sidebar when the case is in the AI Chat
   Sidebar section, otherwise the full-page chat (the Home page). Run both, with a
   `parametrize`, only where behaviour is known to differ between them.
2. **Write the test.** One file per case, named `test_c<ID>_<description>.py`:

   ```python
   import pytest

   from modules.browser_object import SmartBar, SmartWindowChat
   from modules.mock_server import MockServer

   PROMPT = "In one plain sentence with no formatting, what is a group of otters called?"


   @pytest.fixture()
   def test_case():
       return "3374375"


   def test_continue_conversation_in_sidebar(
       smart_window_chat: SmartWindowChat, mock_server: MockServer, driver
   ):
       SmartBar(driver).open_smart_bar()  # or open_full_page_chat()

       chat = smart_window_chat
       chat.send(PROMPT)

       assert chat.get_last_reply() == mock_server.chat_reply_text(PROMPT)
   ```

   - `smart_window_chat` gives you the `SmartWindowChat` BOM with Smart Window active, a
     stand-in FxA token, and the mock server loaded with this test's recording.
   - `chat.send(text)` sends from the Smart Bar and returns once the assistant has finished
     answering, tool calls included. Call it again for a follow-up.
   - `get_last_reply()` and `get_messages()` read what the chat shows;
     `mock_server.chat_reply_text(prompt)` is what the server sent.
   - Ask for plain sentences when you compare reply text, since the chat renders markdown.
3. **Record it** (see below). Without a recording, replay fails and tells you the command.
4. **Review the recording's diff**, then add the test to `manifests/key.yaml` and commit the
   test and its recording together.

## Record a test

**Get a token.** Recording needs a prod Firefox Account token. In a normal Firefox:

1. Sign in to Smart Window.
2. In `about:config`, set `devtools.chrome.enabled` to `true`. Without it the Browser Console
   has no input line.
3. Open the **Browser Console** (Cmd/Ctrl+Shift+J, or Tools → Browser Tools → Browser
   Console). It opens in its own window. Not the Web Console (F12): it can't run this and
   fails with `ChromeUtils is not defined`.
4. Run this. It returns the token:

```js
await (async () => {
  const { getFxAccountsSingleton } = ChromeUtils.importESModule("resource://gre/modules/FxAccounts.sys.mjs");
  const { OAUTH_CLIENT_ID, SCOPE_SMART_WINDOW, SCOPE_PROFILE_UID } = ChromeUtils.importESModule("resource://gre/modules/FxAccountsCommon.sys.mjs");
  const fxa = getFxAccountsSingleton();
  const options = { scope: [SCOPE_SMART_WINDOW, SCOPE_PROFILE_UID], client_id: OAUTH_CLIENT_ID };
  await fxa.removeCachedOAuthToken({ token: await fxa.getOAuthToken(options) });
  return fxa.getOAuthToken(options);
})();
```

The token lasts a few hours. Never commit it or paste it into shared places. It is not the
same as `CI_WAF_TOKEN`, which the FxA sign-in tests use.

**Record:**

```bash
MOZ_FXA_BEARER_TOKEN='<token>' pytest tests/smart_window/test_c<ID>_<description>.py --mock-mode=record
```

To keep the token out of your shell history, put `MOZ_FXA_BEARER_TOKEN=<token>` in a file
outside the repo (for example `~/.starfox-record.env`, readable only by you with
`chmod 600`) and load it:

```bash
set -a; . ~/.starfox-record.env; set +a
pytest tests/smart_window/test_c<ID>_<description>.py --mock-mode=record
```

Or point a VS Code launch configuration at the file with `"envFile"`. When the token expires,
get a new one the same way and replace the line in the file.

**Review the diff before committing.** Look at the `request` entries, any `tool_calls`, and
the reply `content`. Fields that change on every call (ids, timestamps, token counts) and the
proxy's `provider_specific_fields` are left out of saved recordings, so the diff shows only
real changes.
Tool call ids stay, because Firefox needs them.

## When to re-record

You don't need to track this yourself. Replay tells you. The pre-commit hook runs the tests
you commit in replay, and a chat test with no matching recording fails with the fix:

```
This test has no recording yet (data/recordings/smart_window/test_x.json doesn't exist).
Record it with a prod FxA token in MOZ_FXA_BEARER_TOKEN (see SMART_WINDOW_MOCK_SERVER.md):
  pytest "tests/smart_window/test_x.py::test_…" --mock-mode=record
```

That happens for a new test, a changed prompt, or Firefox sending a chat or search request the
recording doesn't have. Changing page objects, selectors or test steps doesn't need a
re-record: the recording holds the model's replies, not Firefox's behaviour.

The hook also fails, before starting Firefox, when a chat test you commit has no recording
file, even one marked `unstable` or `headed`. Tests that build their replies (below) don't need
one. When you commit shared mock-server code (`mock_server.py`, `recording.py`, the Smart
Window page objects or the suite's `conftest.py`), the hook runs every chat test.

## Record or build?

Instead of recording, a test can write the model's replies in code with the builders in
`modules/classes/recording.py`: `chat_reply()`, `tool_call()` and `search_results()`.

- **Record** when the case says "the model does X". You test Firefox against real model
  behaviour.
- **Build** when the case says "when the model returns Y, Firefox does Z": invalid tool calls,
  no-match errors, a long reply, fixed search results. A real model won't produce those on
  demand.

Built replies can't be checked in `live` mode, since live uses the real model. So far only
`chat_reply()` has been tried in Firefox.

## Token usage

`record` and `live` use real LLM tokens, counted against the FxA account's MLPA limits.
After those runs pytest lists the tokens each test used, from the counts MLPA sends with each
reply. Replay sends nothing to MLPA and uses none, so it prints nothing.

```
=============================== LLM token usage ================================
    1,255 tokens (1,200 in, 55 out, 2 requests)  tests/smart_window/test_x.py::test_x  (2.5x recorded)
    1,255 tokens in total
```

- Recording saves the tokens it used in the recording's `meta.usage`, in the format below
  without the first five fields. A later `record` or `live` run that uses at least twice its
  total is flagged, as above: usually a longer prompt or reply.
- Each test also gets an `llm_usage` user property, which ends up in `report.json`
  (`tests[].user_properties`) for dashboards. In `record` and `live` it's the tokens the run
  spent. In `replay`, CI's mode, it's copied from `meta.usage`: what the test used when it was
  recorded on `recorded_at` with Firefox `recorded_firefox_version`, not tokens spent by CI.
  It changes only when the test is re-recorded, so don't add replay figures up as spend. Tests
  whose recording has no `meta.usage` (built with `chat_reply()` and friends, or recorded
  before it was saved) get none.

```json
"llm_usage": {
  "schemaVersion": 1,
  "mode": "live",
  "recorded_at": "2026-10-01",
  "recorded_firefox_version": "159.0a1",
  "recorded_total_tokens": 500,
  "requests": 2,
  "prompt_tokens": 1200,
  "completion_tokens": 55,
  "total_tokens": 1255,
  "by_purpose": {
    "chat": {"model": "gemini-3.1-flash-lite", "requests": 1, "prompt_tokens": 1000, "completion_tokens": 50, "total_tokens": 1050},
    "title-generation": {"model": "qwen3-235b-a22b-instruct-2507-maas", "requests": 1, "prompt_tokens": 200, "completion_tokens": 5, "total_tokens": 205}
  }
}
```

## How it works

- **Prefs.** The suite's `prefs_list` (`tests/smart_window/conftest.py`) sets, for every Smart
  Window test, `browser.smartwindow.endpoint` and `browser.smartwindow.searchQuery.endpointURL`
  to the mock server, and `browser.ml.enable`, without which Firefox sends no LLM requests.
  Other suites are unaffected.
- **Sign-in.** `SmartWindow.stub_fxa_token()` replaces Firefox's FxA token with a stand-in, the
  same trick Firefox's own tests use. In record and live modes the mock server swaps in your
  real token on the way out.
- **Matching.** Each request is reduced to a short summary. Chat messages (streamed requests
  with purpose `chat`) match on prompt and tool round, searches on their query, and everything
  else is a background request (title generation, conversation starters...), matched on its
  purpose alone.
- **Missing entries.** A missing chat or search entry fails the test. A missing background entry
  gets a 503 error; Firefox carries on and the test isn't failed.
- **Firefox versions.** CI tests Firefox Beta, while recordings are often made with Nightly.
  Background requests can differ between versions (some Beta features send purpose `chat`
  without streaming); they're answered with a 503 rather than failing the test.
- **Privacy.** Recordings keep only the allow-listed summary and the response. Tokens, chat
  ids, headers, system prompts and page content are never written.
- **Reading the chat.** The conversation renders in a page Selenium can't reach.
  `SmartWindowChat._chat_script()` runs code inside it; new chat actions go through it too.
- **Waiting.** `chat.send()` counts the messages already sent (from Firefox's own
  conversation), sends, then waits until one more has been fully answered.
- **Format.** The file's wrapper (`meta`, `interactions`, `request`, `response`) is ours; the
  responses inside are the OpenAI Chat Completions format, as MLPA sent them.

## Troubleshooting

| Symptom | Cause |
|---|---|
| "No recording … Record it with …" | The recording is missing an entry. Run the command it prints. |
| "MLPA returned errors: [(401, …)]" | The token has expired or isn't a prod token. Get a new one. |
| "MLPA returned errors: [(429, …)]" | The account hit its MLPA rate limit. Wait, or record fewer tests at once. |
| "needs a prod FxA token in MOZ_FXA_BEARER_TOKEN" | `record` or `live` without a token. |
| `ChromeUtils is not defined` when getting a token | The snippet ran in the Web Console. Use the Browser Console (see Record a test). |
| "No chat reply was served for '…'" | The chat request had no recording; the "No recording" error for the same test has the fix. |
| "The assistant never finished turn N" | No reply arrived in time; usually a failed request. Check the log above it. |
| "Mock server is not answering … title-generation" (INFO) | A background request has no recording. Expected and harmless. |
| model-hub "Forbidden URL" errors in Firefox's output | Automation blocks on-device model downloads. Expected. It's why `submit_chat` picks Ask explicitly. |

## Not covered

- **Auto Tab Grouping (the Organize Tabs panel).** Grouping runs on on-device models that
  automation blocks; only the group naming goes through the LLM.
- **Memories timing.** The 15-minute and 48-hour schedules need control over time, not
  replies.
- **Remote Settings and model-hub** still use the real network. That doesn't affect replay.

## Where things live

| Path | What |
|---|---|
| `modules/mock_server.py` | `MockServer`: replay, forwarding, `chat_reply_text`, `tool_calls`, `usage` |
| `modules/classes/recording.py` | `Recording`, matching, builders |
| `modules/browser_object_smart_window_chat.py` | `SmartWindowChat` BOM |
| `modules/browser_object_smart_bar.py` | `SmartBar`: open the chat, `submit_chat` |
| `tests/smart_window/conftest.py` | Prefs, `mock_server`, `smart_window_chat` |
| `data/recordings/smart_window/` | Recordings, one per test |
