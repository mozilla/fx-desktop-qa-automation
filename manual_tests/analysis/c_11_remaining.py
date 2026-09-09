"""Critical round -- the remaining suites and the residue of partly-covered ones.

Two groups:

1. Suites that rounds 1-3 never touched at all: 103666 (about:keyboard),
   66659 (Copy Link to Highlight), 54271 (Translate selection panel), 2542 (DevTools eager
   evaluation), 1998 (Full screen), 49853 (third-party add-ons), 22801 (language pack
   updates), 5202 (Default Browser Agent), 498 (Geolocation), 1697 (web compat / sharing),
   67 (crash reporter).

2. Critical cases in suites rounds 1-3 did review, but which those rounds left unassessed --
   mostly newer features added since (the Nova search box widget, split view, profile
   switching a11y) and the visual / High Contrast rows those rounds skipped.

Three suite names in crit_pop.py were corrected while working through this batch: 54271 is the
Translate selection panel rather than Picture-in-Picture, 2542 is DevTools eager evaluation
rather than search engines, 5202 is the Default Browser Agent rather than keyboard shortcuts,
and 22801 is language-pack updates rather than notifications.
"""

from _ledger import C
from c_util import CREST

CM = "browser/base/content/test/contextMenu/"
CK = "browser/components/customkeys/tests/browser/"
TRS = "browser/components/translations/tests/browser/"
WC = "devtools/client/webconsole/test/browser/"
SB = "browser/components/urlbar/tests/browser/searchbar/"
PROF = "browser/components/profiles/tests/browser/"
TABS = "browser/components/tabbrowser/test/browser/tabs/"

# ================================================================ about:keyboard (103666)
C(
    103666,
    "STRONG",
    CK + "browser_CustomKeys.js; browser_aboutKeyboard.js",
    "testChangeKey assigns a new shortcut and asserts it is persisted, including the modifier "
    "plus suffix-key sequence this case describes.",
    [4140716],
)
C(
    103666,
    "STRONG",
    CK + "browser_CustomKeys.js",
    "testClearAll clears several shortcuts and testResetAll then restores the defaults, which is "
    "exactly the 'Reset all shortcuts to default after multiple were cleared' sequence.",
    [4140746],
)
C(
    103666,
    "STRONG",
    CK + "browser_aboutKeyboard.js; browser_CustomKeys.js",
    "browser_aboutKeyboard.js asserts the Glean metrics the page records -- page entry, change, "
    "clear, reset and reset_all actions -- alongside testChangeKey / testClearKey / "
    "testClearAll / testResetKey / testResetAll driving each action.",
    [4140734, 4140735, 4140736, 4140737, 4140738],
)

# ================================================================ Copy Link to Highlight (66659)
C(
    66659,
    "STRONG",
    CM
    + "browser_copy_link_to_highlight.js; browser_copy_link_to_highlight_viewsource.js",
    "isVisibleIfSelection, notVisibleIfNoSelection and notVisibleInEditable cover when the item "
    "is offered; copiesToClipboard and copiesCleanLinkToClipboard assert the text-fragment URL "
    "that lands on the clipboard, including the stripped-parameter form.",
    [3079215, 3079172],
)
C(
    66659,
    "STRONG",
    CM + "browser_copy_link_to_highlight.js",
    "removesAllHighlightsWithEmptyFragment and removesAllHighlightsWithNonEmptyFragment cover "
    "Remove Highlight on its own and in combination with copying a new link.",
    [3079216, 3079217],
)
C(
    66659,
    "STRONG",
    CM + "browser_copy_link_to_highlight.js",
    "copiesToClipWithExistingHighlightAndSelection and "
    "copiesToClipWithExistingHighlightAndNoSelection cover copying a link while a highlight is "
    "already present.",
    [3079218],
)

# ================================================================ Translate selection (54271)
C(
    54271,
    "STRONG",
    TRS + "browser_translations_select_context_menu_with_hyperlink.js; "
    "browser_translations_select_context_menu_with_text_selected.js; "
    "browser_translations_select_context_menu_with_no_text_selected.js",
    "A test dedicated to invoking the selection-translation panel from the context menu of a "
    "hyperlink, and another for plain selected text including the no-selection case.",
    [2655221, 2655223],
)
C(
    54271,
    "STRONG",
    TRS
    + "browser_translations_select_panel_pdf.js; browser_translations_select_panel_reader_mode.js",
    "browser_translations_select_panel_pdf.js drives the selection-translation panel over a PDF "
    "in the built-in viewer.",
    [2655225],
)

# ================================================================ DevTools eager eval (2542)
C(
    2542,
    "STRONG",
    WC + "browser_jsterm_eager_evaluation.js; browser_console_eager_eval.js; "
    "browser_console_eager_eval_resolve.js; browser_jsterm_eager_evaluation_warnings.js",
    "browser_jsterm_eager_evaluation.js toggles the instant-evaluation preference and asserts "
    "the preview result appears and updates as the expression is typed.",
    [593668],
)
C(
    2542,
    "STRONG",
    WC + "browser_jsterm_autocomplete_eager_evaluation.js",
    "A test dedicated to the eager-evaluation preview following the selected autocomplete "
    "suggestion.",
    [593720],
)
C(
    2542,
    "STRONG",
    WC
    + "browser_jsterm_eager_evaluation.js; browser_jsterm_eager_evaluation_warnings.js; "
    "browser_jsterm_eager_evaluation_in_debugger_stackframe.js",
    "The eager-evaluation tests cover expressions that must not be evaluated eagerly and the "
    "side-effect guard that prevents a long or looping expression from being run.",
    [593688],
)

# ================================================================ geolocation (498)
C(
    498,
    "STRONG",
    "dom/geolocation/test/mochitest/test_crossorigin_iframe.html; "
    "dom/geolocation/test/browser/browser_geolocation_override.js; "
    "browser/base/content/test/permissions/browser_permission_delegate_geo.js",
    "The secure-context and delegation rules that decide when geolocation is refused are covered "
    "by the permission-delegate and cross-origin tests.",
    [18788],
)

# ================================================================ search box widget (65334)
C(
    65334,
    "STRONG",
    SB
    + "browser_search.js; browser_new_searchbar_init.js; browser_searchbar_context.js",
    "browser_search.js performs a search from the new search box and asserts the resulting load; "
    "browser_new_searchbar_init.js covers the widget's initial state.",
    [3897528],
)
C(
    65334,
    "STRONG",
    SB + "browser_searchbar_customizing_nobreakout.js; browser_searchbarOverflow.js; "
    "browser/components/customizableui/test/browser_901207_searchbar_in_panel.js",
    "Removing the search box widget from the toolbar and its overflow behaviour are covered by "
    "the customising and overflow tests.",
    [3897525],
)
C(
    65334,
    "STRONG",
    SB + "browser_searchbar_addEngine.js; browser_searchbar_addEngineBadge.js; "
    "browser/components/search/test/browser/browser_searchbar_addEngine.js",
    "Adding an OpenSearch engine offered by a page, the badge that advertises it, and searching "
    "with the newly added engine.",
    [3897546, 3897544],
)
C(
    65334,
    "STRONG",
    SB + "browser_searchModeSwitcher.js; browser_resultsMenu.js; "
    "browser/components/search/test/browser/browser_searchbar_default.js",
    "browser_searchModeSwitcher.js drives the Unified Search Button, including which engines it "
    "lists and the default-engine change being reflected in the widget.",
    [3897534, 3897585, 3028818],
)
C(
    65334,
    "STRONG",
    SB
    + "browser_searchbar_keyboard_navigation.js; browser_searchbar_mouseNavigation.js; "
    "browser/components/search/test/browser/browser_searchbar_enter.js",
    "The keyboard and mouse navigation tests cover the modifier-click and modifier-Enter "
    "behaviours -- background tab, new window, and middle-click opening the engine's home page.",
    [3897537, 3897575, 3897588],
)
C(
    65334,
    "STRONG",
    SB + "browser_searchbar_a11y.js; browser_searchbar_actionLabels.js",
    "browser_searchbar_a11y.js asserts the search box's accessible labelling and role, which "
    "includes the localised placeholder.",
    [3897571],
)

# ================================================================ profiles (2119)
C(
    2119,
    "STRONG",
    PROF + "browser_test_profile_selector.js; browser_activate.js; "
    "browser_update_profile_on_window_switch.js; browser_window_title_test.js",
    "The profile selector, activating a profile, and the window following the correct profile on "
    "switch are covered directly -- the substance of launching a profile in a new browser and of "
    "two profiles running side by side.",
    [133392, 295985, 295987],
)
C(
    2119,
    "STRONG",
    PROF
    + "browser_appmenu.js; browser_appmenu_menuitem_updates.js; browser_menubar_profiles.js; "
    "browser_refresh_button.js; browser_notify_changes.js",
    "Restarting into the correct profile from the app menu / about:profiles surface, and the "
    "refresh action, are covered by the app-menu and refresh-button tests.",
    [295989, 295990],
)

# ================================================================ split view (2103)
C(
    2103,
    "STRONG",
    TABS + "browser_tab_splitview.js; browser_tab_splitview_contextmenu.js; "
    "browser_tab_splitview_keyboard_focus.js; browser_tab_splitview_footer.js; "
    "browser_tab_splitview_alt_click.js",
    "Split View has a dedicated test group covering creation from the tab context menu, focus "
    "handling and interacting with each pane -- which is what 'searching is possible after "
    "creating a Split View from the context menu' checks.",
    [3903432],
)

# ================================================================ find toolbar (2085)
C(
    2085,
    "STRONG",
    "toolkit/content/tests/browser/browser_findbar.js; browser_findbar_marks.js; "
    "browser_findbar_hiddenframes.js; browser_findbar_hidden_reveal.js",
    "browser_findbar.js drives find over ordinary and non-trivial page content and asserts the "
    "match count and highlight marks, which covers matching text rendered on buttons and text "
    "containing special characters.",
    [127250, 127275, 127276],
)
C(
    2085,
    "STRONG",
    "browser/base/content/test/general/browser_findbarClose.js; "
    "toolkit/content/tests/browser/browser_findbar.js",
    "browser_findbarClose.js asserts the findbar's state across navigation, including back and "
    "forward.",
    [127261],
)

# ================================================================ reviewed but kept
CREST(
    66659,
    "MEDIUM",
    CM + "browser_copy_link_to_highlight.js",
    "The Ctrl/Cmd-modified and Ctrl/Cmd+A (select-all) selection variants are not covered -- the "
    "in-tree tests build the selection programmatically rather than through those key "
    "combinations.",
)
CREST(
    54271,
    "MEDIUM",
    TRS + "browser_translations_select_panel_script_tags.js",
    "Left over: invoking the panel from an image with an embedded link, and the panel's layout "
    "for a single word and for a very long paragraph. The panel's translation behaviour is well "
    "covered, but not those presentation cases.",
)
CREST(
    2542,
    "MEDIUM",
    WC + "browser_jsterm_eager_evaluation.js",
    "The Space / Delete key behaviour in the eager-evaluation input is not asserted.",
)
CREST(
    1998,
    "MEDIUM",
    "browser/base/content/test/fullscreen/browser_fullscreen_menus.js; browser_fullscreen_warning.js",
    "Full-screen chrome behaviour is covered for menus, the warning overlay and keyboard "
    "handling, but these rows are about the title bar and toolbars being re-activatable in full "
    "screen and the window controls rendering correctly, including under RTL and High Contrast -- "
    "window-decoration checks the harness cannot make.",
)
CREST(
    49853,
    "MEDIUM",
    "n/a",
    "Third-party applications: GNOME Shell extensions installed through extensions.gnome.org, and "
    "KeePassXC plus its browser connector exchanging passwords. Both need the external "
    "application installed and running.",
)
CREST(
    22801,
    "MEDIUM",
    "toolkit/mozapps/extensions/test/xpcshell/test_webextension_langpack.js; "
    "test_signed_langpack.js; test_distribution_langpack.js",
    "Language packs being updated across a dot release, a release update and a beta update, and "
    "the pack applying to the crash reporter. Each needs a real update from one build to another.",
)
CREST(
    5202,
    "MEDIUM",
    "toolkit/mozapps/defaultagent/",
    "The Windows Default Browser Agent: pingsender POST requests, disabling the agent by pref, "
    "and pre-release telemetry upload on late-beta builds. The agent is a separate executable "
    "driven by Task Scheduler, with no test harness in the tree.",
)
CREST(
    498,
    "MEDIUM",
    "dom/geolocation/test/",
    "Sharing location with live third-party sites that consume geolocation.",
)
CREST(
    1697,
    "MEDIUM",
    "browser/base/content/test/webrtc/",
    "A Twilio Video SDK web-compat regression, which needs the live third-party SDK, and the "
    "global sharing overlay's message and position when the shared screen changes.",
)
CREST(
    67,
    "MEDIUM",
    "toolkit/crashreporter/test/",
    "The crash reporter: the dialog appearing after a crash, reports stored locally, unsubmitted "
    "reports being generated and submitted to Socorro, and the dialog's localisation. These need "
    "a real crash and a live Socorro endpoint.",
)
CREST(
    65334,
    "MEDIUM",
    SB + "browser_search.js; browser_searchModeSwitcher.js",
    "Remaining search-box rows: suggestions in normal and private browsing, searches not being "
    "written to history in PBM, aliases that should and should not resolve, quick actions being "
    "absent, URL navigation being refused, High Contrast rendering, live language switching, and "
    "the widget under window resize. The widget's core search path is covered but these "
    "behavioural exclusions are not.",
)
CREST(
    2119,
    "MEDIUM",
    PROF + "browser_test_profile_selector.js; toolkit/profile/test/",
    "Left over: the Profile Manager with a custom folder, command-line and terminal profile "
    "creation, --first-startup, recovering data from a deleted profile, Troubleshoot Mode with "
    "add-ons disabled, about:support's Refresh, the DevEdition profile, Work Offline, and the "
    "Profile Switching High Contrast and screen-reader rows.",
)
CREST(
    2103,
    "MEDIUM",
    TABS + "browser_tab_splitview.js",
    "PiP initiated from Split View, pinned-tab content refreshing after a crash, the two tab-group "
    "onboarding flows, and tab hover previews across screen resolutions including hiDPI.",
)
CREST(
    43517,
    "MEDIUM",
    "toolkit/components/passwordmgr/test/browser/",
    "CSV export of synced passwords and opening that file in the OS text editor, the password "
    "manager against three live sites (mail.ru, reddit.com, netflix.com), and Sync combined with "
    "a Primary Password.",
)
CREST(
    53810,
    "MEDIUM",
    "browser/components/sidebar/tests/browser/",
    "Sidebar open/close animation and the width of the search box in the synced-tabs panel -- both "
    "presentation details.",
)
CREST(
    29219,
    "MEDIUM",
    "browser/components/downloads/test/browser/",
    "The downloads panel under High Contrast, and one case already marked [On Hold] in TestRail.",
)
CREST(
    943,
    "MEDIUM",
    "browser/components/screenshots/tests/browser/",
    "The Screenshots UI under High Contrast themes.",
)
CREST(
    2085,
    "MEDIUM",
    "toolkit/content/tests/browser/browser_findbar.js",
    "Find over an RTL-language page and over a plain .txt document.",
)
CREST(
    70723,
    "MEDIUM",
    "browser/components/tabbrowser/test/browser/tabs/",
    "Tab Notes rows about the original-title shadow placeholder, reverting a cleared name on blur, "
    "and renaming a tab with a screen reader.",
)
