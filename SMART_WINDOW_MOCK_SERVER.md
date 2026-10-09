# Smart Window Mock Server

Smart Window chat tests never talk to the real LLM service (MLPA). Firefox sends its chat
and web search requests to a local mock server, which answers with responses recorded
earlier. Tests get the same replies on every run, need no account, and take seconds.

```
test → BOMs (SmartBar, SmartWindowChat, TabBar) → Firefox
Firefox ──(endpoint prefs)──► MockServer ──► replay: data/recordings/... JSON
                                       └──► record / live: stage MLPA, with your token
```

Everything Firefox does with a reply is still real: running tools, showing cards, grouping
tabs, rendering. Only the model's replies come from the recording.

## Get started

Run the existing chat tests. No token or setup is needed:

```bash
pytest tests/smart_window/test_c3374375_continue_conversation_in_sidebar.py
pytest tests/smart_window/test_c4438277_group_related_tabs.py
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

**Get a token.** Recording needs a prod Firefox Account token. Sign in to Smart Window in a
normal Firefox, open the Browser Console (Cmd/Ctrl+Shift+J) and run:

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
outside the repo (for example `~/.starfox-record.env`) and load it, or point a VS Code launch
configuration at it with `"envFile"`.

**Review the diff before committing.** Look at the `request` entries, any `tool_calls`, and
the reply `content`. Fields that change on every call (ids, timestamps, token counts, Gemini's
thought signatures) are left out of saved recordings, so the diff shows only real changes.
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

## Tab management tests

Tab actions (group, close and so on) are chat tests whose replies are tool calls. See
`tests/smart_window/test_c4438277_group_related_tabs.py`.

- Describe the scenario with `TabGroupingScenario` (`modules/classes/tab_grouping_scenario.py`):
  the instruction, the pages to open as tabs, and the pages expected in the group.
- Pages are small HTML files in `data/smart_window_pages/`. The `tab_pages` fixture serves them
  and turns file names into URLs; open them with
  `TabBar.open_urls_in_tabs(..., open_first_in_current_tab=True)`. They're kept out of
  `data/pages/` because some tests copy every file in that folder.
- After `chat.send(...)`:
  - `mock_server.tool_calls("manage_tabs")` is what the model asked Firefox to do;
  - `chat.confirm_tab_grouping_if_asked()` clicks Confirm if the model asked first;
  - `TabBar.expect_tab_group_exists()` waits for the group;
  - `scenario.check_grouping(...)` reports tabs Firefox left out separately from tabs the model
    chose wrongly.

The model only sees each tab's title and a URL token built from the host and path (for example
`LOCALHOST_LASAGNA_HTML_1`), not the page content, unless it calls `get_page_content`.

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
| "needs a prod FxA token in MOZ_FXA_BEARER_TOKEN" | `record` or `live` without a token. |
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
| `modules/mock_server.py` | `MockServer`: replay, forwarding, `chat_reply_text`, `tool_calls` |
| `modules/classes/recording.py` | `Recording`, matching, builders |
| `modules/browser_object_smart_window_chat.py` | `SmartWindowChat` BOM |
| `modules/browser_object_smart_bar.py` | `SmartBar`: open the chat, `submit_chat` |
| `modules/classes/tab_grouping_scenario.py` | `TabGroupingScenario` |
| `tests/smart_window/conftest.py` | Prefs, `mock_server`, `smart_window_chat`, `tab_pages` |
| `data/recordings/smart_window/` | Recordings, one per test |
| `data/smart_window_pages/` | Pages opened as tabs |
