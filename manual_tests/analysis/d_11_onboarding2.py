from _ledger import C, CSEC

# ---------------------------------------------------------------- suite 103289
# "Onboarding" (75 cases) - a second, newer Smart-Window onboarding suite. Its cases are
# near-verbatim duplicates of suite 70279's, so they map to the same in-tree tests.
CSEC(
    103289,
    "STRONG",
    "browser/components/aiwindow/ui/test/browser/browser_aiwindow_firstrun.js; browser_open_aiwindow.js; "
    "browser_aiwindow_account_auth.js; browser_smartwindow_init.js; browser_smartwindow_nimbus.js; "
    "browser_aiwindow_switcher.js; browser_smartwindow_classic_mode_switch.js; browser_smartwindow_prompts.js; "
    "browser_smartwindow_history_commands.js; browser_smartwindow_history_thumbnails.js; "
    "browser_aiwindow_session_restore.js; browser_smartwindow_default_startup.js; "
    "browser_aiwindow_memories.js; browser_aiwindow_applied_memories_button.js; "
    "browser_aiwindow_smartbar.js; browser_aiwindow_smartbar_suggestions.js; "
    "browser_aiwindow_smartbar_context_chips.js; browser_smartwindow_smartbar_model_select.js; "
    "browser_smartwindow_manage_tabs_tool.js; browser_aiwindow_group_tabs_button.js; "
    "browser_sidebar_aiwindow.js; browser_aiwindow_ask_button.js; browser_security_chat.js; "
    "browser/components/aiwindow/models/tests/browser/browser_conversation.js; browser_conversation_starters.js",
    "DUPLICATE SUITE: sections 938697-938705 repeat suite 70279's Smart Window onboarding, "
    "window switching, quick prompts, history, session restore, memories, chat sidebar, smart bar "
    "and settings cases almost verbatim. All of them map to the same ~140 in-tree aiwindow tests. "
    "Recommendation: this whole suite is a de-duplication candidate independent of automation "
    "coverage - it duplicates 70279.",
    [938697, 938698, 938699, 938700, 938701, 938702, 938703, 938704, 938705],
)

# ---------------------------------------------------------------- suite 59371
# "Terms of Service / Terms of Use onboarding" (75 cases).
# VERIFIED: there is NO in-tree test for the ToU/ToS onboarding modal itself - searching the
# whole tree for termsofuse/TermsOfUse returns only the localisation file
# browser/locales/en-US/browser/termsofuse.ftl. The modal, its bypass-resistance, its
# drop-downs, its pref migration across builds and the "no telemetry before acceptance" rule
# are manual-only. Only the Preferences > Privacy data-collection controls have a counterpart.
C(
    59371,
    "STRONG",
    "browser/components/preferences/tests/privacy/browser_privacy_uploadEnabled.js; "
    "browser_privacypane_2.js; browser_privacypane_3.js; browser_privacy_segmentation_pref.js; "
    "browser/components/preferences/tests/browser_bug731866.js",
    "The Firefox Data Collection and Use checkboxes in about:preferences#privacy - technical and "
    "interaction data, daily usage ping, studies, personalised extension recommendations and "
    "automatic crash reports - and the pref each one writes.",
    [2888476, 2838450, 2888478, 2888553, 2888706, 2888707],
)
C(
    59371,
    "MEDIUM",
    "browser/components/aboutwelcome/tests/browser/browser_aboutwelcome_multistage_mr.js; "
    "browser/components/asrouter/tests/browser/browser_asrouter_targeting.js",
    "The ToU modal itself has no in-tree test (verified). The Glean/telemetry cases, a11y matrix, "
    "bypass-resistance cases, pref-migration-across-builds cases and the learn-more link "
    "destinations all stay manual.",
    [2838448, 2838449, 2838442, 2838443, 2838444, 2838445, 2838446, 2889830, 2888555,
     2887703, 2889834, 2889835, 2888572, 2887125, 2888566],
)

# ---------------------------------------------------------------- suite 76427
# "ToU onboarding on Linux distributions" (9 cases) - rpm / deb / snap / flatpak packaging
# plus distribution.ini handling. No in-tree analog: packaging and distribution config are
# build/OS integration, and the ToU modal itself is untested upstream.
C(
    76427,
    "MEDIUM",
    "browser/installer/; toolkit/mozapps/installer/",
    "Distribution-channel packaging is built but not behaviourally tested in the tree, and the "
    "ToU prompt has no in-tree test at all.",
    [3989461, 3408308, 3408307, 3408306, 3989414, 3989413, 3989415, 3408304, 3408305],
)