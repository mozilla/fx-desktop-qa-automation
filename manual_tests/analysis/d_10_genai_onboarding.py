from _ledger import C, CSEC

# ---------------------------------------------------------------- suite 70279
# "AI window / Smart Window" (175 cases). Tree: browser/components/aiwindow/ui/test/browser/
# (124) + browser/components/aiwindow/models/tests/browser/ (16) + browser/components/genai/
# tests/browser/ (18). This is one of the most heavily automated areas in the tree.
C(
    70279,
    "STRONG",
    "browser/components/aiwindow/ui/test/browser/browser_aiwindow_firstrun.js; browser_open_aiwindow.js; "
    "browser_aiwindow_integration.js; browser_aiwindow_account_auth.js; browser_smartwindow_init.js; "
    "browser_smartwindow_nimbus.js; browser_smartwindow_disclaimer.js; browser_smartwindow_beta_badge.js; "
    "browser/components/uitour/test/browser_UITour_aiwindow.js; "
    "toolkit/components/messaging-system/schemas/SpecialMessageActionSchemas/test/browser/"
    "browser_sma_fxa_aiwindow_signin_flow.js",
    "The onboarding flow end to end, its entry points, the signed-in vs signed-out variants, the "
    "FxA sign-in hand-off, the ToU modal and the enrolment/Nimbus gating.",
    [3240165, 3371298, 3371299, 3371305, 3371313, 3371734, 3372090, 3374158, 3914754,
     3371631, 4062285],
)
C(
    70279,
    "STRONG",
    "browser/components/aiwindow/ui/test/browser/browser_aiwindow_smartbar.js; browser_aiwindow_smartbar_ask.js; "
    "browser_aiwindow_smartbar_autofill.js; browser_aiwindow_smartbar_suggestions.js; "
    "browser_aiwindow_smartbar_quicksuggest.js; browser_aiwindow_smartbar_interactions.js; "
    "browser_aiwindow_smartbar_focus.js; browser_aiwindow_smartbar_placeholder.js; "
    "browser_aiwindow_smartbar_input_cta.js; browser_aiwindow_smartbar_tab_switch.js; "
    "browser_aiwindow_smartbar_chat_active_navigate.js; browser_smartwindow_smartbar_glow.js; "
    "browser_run_search_back_navigation.js; browser_smartwindow_run_search.js; "
    "browser/components/aiwindow/models/tests/browser/browser_search_the_web.js",
    "The Smart Bar: the Ask/Go dropdown, domain autocomplete, suggestions and intent detection, "
    "classic search, searching with a chosen engine, and being redirected to an already-open tab.",
    [3321887, 3240174, 3240369, 3248361, 3248362, 3321894, 3321908, 3321909, 3321910,
     3977124, 3977126],
)
C(
    70279,
    "STRONG",
    "browser/components/aiwindow/ui/test/browser/browser_aiwindow_smartbar_context_chips.js; "
    "browser_aiwindow_smartbar_inline_mentions.js; browser_aiwindow_kit_mention.js; browser_aiwindow_grouped_chips.js; "
    "browser_aiwindow_website_chip.js; browser_aiwindow_website_select.js; browser_aiwindow_website_confirmation.js; "
    "browser_smartwindow_smartbar_mentions_filter.js; browser_aiwindow_smartbar_context_paste.js",
    "@-mentioning one or several open tabs in the Smart Bar, the resulting context chips, deleting "
    "a chip with backspace or its close button, the maximum chip count, and clicking a chip to "
    "jump to that tab.",
    [3322032, 3322033, 3322034, 3322035, 3322036, 3322041, 3322037, 3322039, 3322040, 3322042],
)
C(
    70279,
    "STRONG",
    "browser/components/aiwindow/ui/test/browser/browser_smartwindow_smartbar_model_select.js; "
    "browser_smartwindow_smartbar_tab_state.js; browser_aiwindow_aifeature_contract.js",
    "Changing the AI model from the Smart Bar, per-tab model switching, the default model not "
    "changing, reaching model preferences from the dropdown, and a Settings change propagating to "
    "open tabs.",
    [3977127, 3977128, 4062274, 4062275, 4062277, 4114597],
)
C(
    70279,
    "STRONG",
    "browser/components/aiwindow/ui/test/browser/browser_aiwindow_switcher.js; "
    "browser_smartwindow_classic_mode_switch.js; browser_smartwindow_switcher_telemetry.js; "
    "browser_smartwindow_default_cmd_n.js; browser_smartwindow_default_startup.js; "
    "browser_aiwindow_immersive.js; browser_smartwindow_tab_move.js; browser_smartwindow_tab_switching.js",
    "The Switch Windows button in both directions, switching while a page is loaded or a response "
    "is streaming, opening a Smart / Classic / Private window from the hamburger menu, reopening a "
    "tab in the other window type, opening links across window types, and the Smart-Window-first "
    "startup rule.",
    [3248785, 3248786, 3309849, 3309850, 3309852, 3309853, 3309854, 3309855, 3309856,
     3309857, 3309858, 3309868, 4062295, 3309851],
)
C(
    70279,
    "STRONG",
    "browser/components/aiwindow/ui/test/browser/browser_aiwindow_memories.js; "
    "browser_aiwindow_memories_toggle_prefs.js; browser_aiwindow_applied_memories_button.js; "
    "browser_memories_icon_button.js; browser_smartwindow_tab_switching_memories.js; "
    "browser_smartwindow_retry_context.js; browser_security_get_user_memories.js",
    "Memories: the Applied-Memories menu auto-opening and its button, toggling memories on/off from "
    "the chat sidebar and the new-tab Smart Bar, the new-memory cards and Save/Don't Save, the "
    "saved-memory notification and deleting from it, retry-without-memories, and memories being "
    "reapplied afterwards.",
    [3240169, 3210817, 3210936, 3210816, 3210818, 3210820, 3210918, 3310496, 3310497,
     3311609, 3332349, 3375055],
)
C(
    70279,
    "STRONG",
    "browser/components/aiwindow/ui/test/browser/browser_smartwindow_prompts.js; "
    "browser/components/aiwindow/models/tests/browser/browser_conversation_starters.js; "
    "browser_smartwindow_tab_switching_starters.js; browser_smartwindow_conversation_state.js; "
    "browser/components/aiwindow/models/tests/browser/browser_conversation.js",
    "Quick Prompts on the home page and in the chat sidebar: the fresh-profile empty state, the "
    "tab-null state, prompts derived from memories and open tabs, dynamic refresh, and follow-up "
    "conversations.",
    [3210778, 3210781, 3210786, 3248360, 3374374, 3210782, 3210783, 3210785, 3210787,
     3374375],
)
C(
    70279,
    "STRONG",
    "browser/components/aiwindow/ui/test/browser/browser_sidebar_aiwindow.js; browser_smartwindow_sidebar.js; "
    "browser_smartwindow_sidebar_prefs.js; browser_smartwindow_sidebar_auto_open_pref_prompt.js; "
    "browser_aiwindow_ask_button.js; browser_aichat_open_link.js; browser_aichat_same_link_click.js; "
    "browser_aiwindow_new_chat_button.js; browser_smartwindow_jump_to_bottom.js; "
    "browser_aichat_content_scrolling_position.js; browser_aiwindow_stop_generation.js; "
    "browser_smartwindow_abort_on_tab_close.js",
    "The AI chat sidebar: open/close from the Ask button and the X, opening assistant links in new "
    "tabs, the new-chat prompt on topic change, Jump to bottom, and stopping generation.",
    [3311329, 3321463, 3240170, 3978359, 3978360, 3322038],
)
C(
    70279,
    "STRONG",
    "browser/components/aiwindow/ui/test/browser/browser_security_chat.js; browser_security_run_search.js; "
    "browser_security_get_open_tabs.js; browser_security_search_browsing_history.js; browser_aiwindow_url_security.js; "
    "browser/components/aiwindow/models/tests/browser/browser_tools_get_page_content.js; "
    "browser_smartwindow_get_page_content_timeout.js",
    "The assistant not acting on the user's behalf, the security boundaries on its tools, and page "
    "content retrieval once a site is unblocked.",
    [3248624, 3914755],
)
C(
    70279,
    "STRONG",
    "browser/components/aiwindow/ui/test/browser/browser_smartwindow_history_commands.js; "
    "browser_aiwindow_history_menu.js; browser_smartwindow_recentchats.js; browser_smartwindow_sanitize.js; "
    "browser_smartwindow_history_thumbnails.js; browser_search_the_web.js; "
    "browser/components/aiwindow/models/tests/browser/browser_search_the_web.js",
    "Reaching the History page and Chat History from the home page, hamburger menu and title menu, "
    "searching history through the assistant, the history summary, the no-results response, and "
    "deleting chat/message history from Clear Browsing Data.",
    [3313455, 3240171, 3240172, 3240173, 3241372, 3313457, 3313459, 3313619, 3313620,
     3320964, 3313456, 3313458],
)
C(
    70279,
    "STRONG",
    "browser/components/aiwindow/ui/test/browser/browser_aiwindow_session_restore.js; "
    "browser_smartwindow_default_startup.js",
    "The Smart Window being restored after restart, after a normal close-and-reopen, and via "
    "'Open previous windows and tabs'.",
    [3309859, 3309860, 3309861, 4065796],
)
C(
    70279,
    "STRONG",
    "browser/components/aiwindow/ui/test/browser/browser_aiwindow_aifeature_contract.js; "
    "browser_smartwindow_nimbus.js; browser_aiwindow_memories.js; browser_aiwindow_theme.js; "
    "browser/components/genai/tests/browser/browser_genai_init.js; browser_chat_nimbus.js",
    "The AI controls settings page: enabling/blocking the Smart Window, the model type shown, "
    "managing and deleting memories (individually and all), changing or setting a custom model "
    "(including mid-conversation), the theme, and the enterprise-policy block.",
    [3310319, 3310316, 3310317, 3252938, 3252940, 3310318, 3252944, 3252942, 3917535,
     3309867],
)
C(
    70279,
    "STRONG",
    "browser/components/aiwindow/ui/test/browser/browser_aiwindow_group_tabs_button.js; "
    "browser_smartwindow_manage_tabs_tool.js; browser_smartwindow_topsites.js; "
    "browser_aiwindow_smartbar_keyboard_navigation.js; browser_smartwindow_chat_browser_tabbable.js",
    "The Similar-Tabs CTA / group-tabs entry point and keyboard access to the Smart Bar and chat.",
    [3240162, 3240133, 3240163, 3349918, 3349912],
)
C(
    70279,
    "STRONG",
    "browser/components/aiwindow/ui/test/browser/browser_smartwindow_telemetry.js; "
    "browser_smartwindow_metrics_telemetry.js; browser_smartwindow_request_response_telemetry.js; "
    "browser_aiwindow_smartbar_telemetry.js; browser_smartwindow_switcher_telemetry.js; "
    "browser_smartwindow_client_error_telemetry.js; browser_smartwindow_uitool_telemetry.js; "
    "browser_smartwindow_history_thumbnails_telemetry.js",
    "The Smart Window telemetry surface (8 dedicated tests).",
    [3311023, 3311024],
)
C(
    70279,
    "MEDIUM",
    "browser/components/aiwindow/ui/test/browser/browser_aiwindow_firstrun.js; browser_smartwindow_footer.js; "
    "browser_smartwindow_panel_list.js",
    "The 24 a11y cases (keyboard / HCM / screen reader per surface), the 24 FxA sign-in matrix "
    "cases (passwordless, TOTP, recovery code/phone, ARK reset flows - these need live accounts), "
    "the Firefox View 'Open in Smart Window' items, and the memory-retention-after-history-deletion "
    "cases are not covered at this altitude in-tree.",
    [3310320, 3374924, 3374925,
     3320965, 3320966, 3321369, 3321370,
     3349900, 3349901, 3349902, 3349903, 3349904, 3349905, 3349906, 3349907, 3349908,
     3349909, 3349910, 3349911, 3349913, 3349914, 3349915, 3349916, 3349917, 3349919,
     3349920, 3977130, 3977131, 3977132, 3977133, 3977134, 3977135, 3978361, 3978362,
     3978363, 3978365,
     3392577, 3392578, 3392579, 3392580, 3392581, 3392582, 3392583, 3392584, 3392585,
     3392586, 3392587, 3392588, 3392589, 3392590, 3392591, 3392592, 3392593, 3392594,
     3392595, 3392596, 3392597, 3392598, 3392599, 3392600],
)

# ---------------------------------------------------------------- suites 23035 / 59371 / 103289 / 76427
# Onboarding: "Easy Setup" (155), "Terms of Service onboarding" (75), "Onboarding" (75),
# "ToU onboarding Fedora" (9). Tree: browser/components/aboutwelcome/tests/browser/ +
# browser/components/asrouter/tests/browser/.
#
# IMPORTANT SHAPE: suite 23035 is a platform/channel matrix - the same ~11 slides
# (Easy Setup, Choose Your Language, Import Browser Data, Mobile Cross-Promotion, Introduce
# AMO, MR Gratitude, pinned/default permutations, dark theme, upgrade spotlight) repeated
# across ~5 platform blocks. The slide mechanics are automated; the repetition is not.
CSEC(
    23035,
    "STRONG",
    "browser/components/aboutwelcome/tests/browser/browser_aboutwelcome_multistage_mr.js; "
    "browser_aboutwelcome_multiselect.js; browser_aboutwelcome_screen_targeting.js; "
    "browser_aboutwelcome_configurable_ui.js; browser_aboutwelcome_import.js; "
    "browser_aboutwelcome_multistage_languageSwitcher.js; browser_aboutwelcome_mobile_downloads.js; "
    "browser_aboutwelcome_multistage_addonspicker.js; browser_aboutwelcome_glean.js; "
    "browser/components/asrouter/tests/browser/browser_asrouter_targeting.js",
    "MATRIX: every slide in this suite has a dedicated in-tree test - the multistage MR flow and "
    "its multiselect checkboxes, the language-mismatch switcher (including the "
    "does-not-appear-without-mismatch case), the import-data slide and its loading/success states, "
    "the mobile QR slide and Skip, the AMO add-ons picker, and the gratitude/Start-browsing slide. "
    "The suite then repeats all of them per platform block. Recommendation: keep ONE platform "
    "block in the crunch-time run and de-prioritise the duplicates; keep the pinned/default-browser "
    "permutations, which are OS state the tree cannot set.",
    [439115, 439116, 439117, 439118, 439119, 439120, 439121, 439122, 439123, 439136,
     439142, 439143, 439144, 439145, 439146, 439147, 439148, 439149, 439150, 439162,
     439168, 439169, 439170, 439171, 439172, 439173, 439174, 439184],
)
C(
    23035,
    "STRONG",
    "browser/components/asrouter/tests/browser/browser_asrouter_experimentsAPILoader.js; "
    "browser/components/aboutwelcome/tests/browser/browser_aboutwelcome_upgrade_multistage_mr.js; browser/components/asrouter/tests/browser/browser_multistage_spotlight.js",
    "The upgrade spotlight not being shown after an update.",
    [2342058, 2342059],
)
C(
    23035,
    "MEDIUM",
    "browser/components/aboutwelcome/tests/browser/browser_aboutwelcome_multistage_mr.js",
    "The pinned / default-browser permutation blocks depend on OS state that browser-chrome does "
    "not manipulate, so they stay manual.",
    [2342051, 2342052, 2342053, 2342054, 2342134, 2342135, 2342136, 2342137, 2342183, 2342184],
)
