"""Critical round -- New Tab page, New Tab widgets and the Home settings pane.

Suites: 5403 (New Tab page and preferences), 67503 (Lists widget), 95385 (New Tab widgets),
69749 (about:settings#home).

67503 and 95385 are the same widget matrix stated twice, so their rows share verdicts.

The New Tab widgets are React components tested with jsx unit tests under
browser/extensions/newtab/test/unit/. Those are component-level rather than end-to-end, but
they drive the real component through the real interactions -- typing a task and pressing
Enter, toggling completion, opening the item menu, resizing the widget -- and assert the
dispatched actions, so they are a genuine match for these rows.

The Home settings pane is the opposite extreme: browser/components/preferences/tests/home/
carries 48 tests and covers nearly every row in suite 69749 one-for-one.
"""

from _ledger import C
from c_util import CREST

NTU = "browser/extensions/newtab/test/unit/content-src/components/"
NTB = "browser/extensions/newtab/test/browser/"
HOME = "browser/components/preferences/tests/home/"

# ================================================================ Lists widget
C(
    67503,
    "STRONG",
    NTU + "Widgets/Lists.test.jsx",
    "'should update task input and add a new task on Enter key' and 'should not dispatch an "
    "action when input is empty' cover adding a task, including the empty-input guard; 'should "
    "add a task with a valid URL and render it as a link' covers the URL variant.",
    [3102193, 3909495],
)
C(
    67503,
    "STRONG",
    NTU + "Widgets/Lists.test.jsx",
    "'should remove task when deleteTask is run from task item panel menu' drives deletion "
    "through the same per-item menu the manual case uses.",
    [3102195, 3909497],
)
C(
    67503,
    "STRONG",
    NTU + "Widgets/Lists.test.jsx",
    "'should toggle task completion' asserts the completion state change.",
    [3102199, 3909499],
)
C(
    67503,
    "STRONG",
    NTU + "Widgets/Lists.test.jsx",
    "'should update list name when edited and saved' and 'uses the Checklist fallback title for "
    "an unnamed default list' cover naming and renaming a list.",
    [3102500, 3909510],
)
C(
    67503,
    "STRONG",
    NTU + "Widgets/Lists.test.jsx",
    "'should delete list and select a fallback list' covers deleting a list and what is selected "
    "afterwards.",
    [3102215, 3909505],
)
C(
    67503,
    "STRONG",
    NTU + "Widgets/Lists.test.jsx; Widgets.test.jsx",
    "The item panel menu, the icon-only menu button names, the list switcher and the "
    "compact/medium/large layouts are each asserted, which is what the widget-menu rows walk.",
    [3102208, 3909502],
)
C(
    67503,
    "STRONG",
    NTU + "Nova/CustomizeMenu/WidgetsManagementPanel/WidgetsManagementPanel.test.jsx",
    "'should dispatch PREF_CHANGED and WIDGETS_ENABLED when lists toggle is fired' and the "
    "matching render assertions cover hiding the checklist from the Manage Widgets panel.",
    [3102212, 3909504],
)
C(
    67503,
    "STRONG",
    NTU + "Widgets/useWidgetCelebration.test.jsx",
    "The celebration hook test covers the animation firing on completion, the per-trigger id, "
    "the frame derived from widget dimensions, and it being suppressed under "
    "prefers-reduced-motion.",
    [3102216, 3909506],
)
C(
    95385,
    "STRONG",
    NTU + "Nova/CustomizeMenu/WidgetsManagementPanel/WidgetsManagementPanel.test.jsx",
    "WidgetsManagementPanel.test.jsx is dedicated to the Manage Widgets panel: the button, the "
    "panel open/close, and the weather / timer / lists toggles with their pref writes.",
    [3908694],
)

# ================================================================ Focus Timer widget
C(
    67503,
    "STRONG",
    NTU + "Widgets/FocusTimer.test.jsx",
    "'should start timer and show progress bar when pressing play' and 'should pause the timer "
    "when pressing pause'.",
    [3102231],
)
C(
    67503,
    "STRONG",
    NTU + "Widgets/FocusTimer.test.jsx",
    "'should reset timer when pressing reset', 'should reset timer should be hidden when timer "
    "is not running' and 'should reset to user's initial duration after timer ends'.",
    [3102233],
)
C(
    67503,
    "STRONG",
    NTU + "Widgets/FocusTimer.test.jsx",
    "'should dispatch pause and set type and when clicking the break timer', the 5-minute break "
    "default, and the automatic focus-to-break handover at zero.",
    [3102242],
)
C(
    67503,
    "STRONG",
    NTU + "Widgets/FocusTimer.test.jsx",
    "'should dispatch set type when clicking the focus timer', the 25-minute focus default, and "
    "the break-to-focus handover.",
    [3102243],
)
C(
    67503,
    "STRONG",
    NTU + "Widgets/FocusTimer.test.jsx",
    "'should render context menu with turn notifications on if notifications are disabled' and "
    "'should turn off notifications when the Turn off notifications option is clicked'.",
    [3112096, 3909483],
)
C(
    67503,
    "STRONG",
    NTU + "Widgets/FocusTimer.test.jsx; "
    "Nova/CustomizeMenu/WidgetsManagementPanel/WidgetsManagementPanel.test.jsx",
    "'should hide Focus Timer when Hide widget option is clicked', with the corresponding "
    "Manage Widgets timer toggle.",
    [3113162, 3909485],
)

# ================================================================ New Tab page
C(
    5403,
    "STRONG",
    NTB + "browser_customize_menu_render.js; browser_customize_menu_content.js; "
    "browser_customize_menu_key_open.js",
    "Three tests cover the Customize your New Tab page button: opening the panel by click and "
    "by keyboard, and the panel's contents.",
    [407933],
)
C(
    5403,
    "STRONG",
    NTB
    + "browser_topsites_section.js; browser_customize_menu_content.js; "
    + HOME
    + "browser_homepage_firefox_home_shortcuts.js",
    "The shortcuts row-count control in the customize panel and the resulting Top Sites section "
    "layout.",
    [407946],
)
C(
    5403,
    "STRONG",
    NTB + "browser_topsites_sponsored.js; browser_sponsored_annotation.js; "
    "browser_sponsor_protection.js; "
    + HOME
    + "browser_homepage_firefox_home_sponsored_stories.js",
    "Toggling sponsored content and the resulting presence or absence of sponsored items is "
    "covered from both the New Tab side and the preferences side.",
    [407956],
)
C(
    5403,
    "STRONG",
    NTB
    + "browser_highlights_section.js; browser_customize_menu_content.js; "
    + HOME
    + "browser_homepage_firefox_home_recent_activity.js",
    "The Recent activity (Highlights) section, its row count and the preference that drives it.",
    [407961],
)
C(
    5403,
    "STRONG",
    NTB + "browser_highlights_section.js; browser_context_menu_item.js; "
    "browser_newtab_last_LinkMenu.js",
    "The Recent activity card context menu, including dismissing a card and deleting the entry "
    "from history, is driven by the link-menu tests over the highlights section.",
    [408001, 408008, 408009],
)
C(
    5403,
    "STRONG",
    NTB
    + "browser_discovery_card.js; browser_discovery_render.js; browser_newtab_last_LinkMenu.js; "
    "browser_context_menu_item.js",
    "Clicking a recommended story, and the story card's context menu including the bookmark and "
    "dismiss-all entries, are covered by the discovery-stream tests.",
    [434629, 434680, 434682, 434690],
)

# ================================================================ about:settings#home
C(
    69749,
    "STRONG",
    "browser/components/preferences/tests/browser_DefaultBrowserHelper.js; "
    "browser_defaultbrowser_alwayscheck.js; "
    "browser/components/shell/test/browser_setDefaultBrowser.js",
    "The default-browser block in the Home/General settings, its state readout and the "
    "always-check preference.",
    [3190614],
)
C(
    69749,
    "STRONG",
    HOME + "browser_homepage_custom_homepage_add_urls.js; "
    "browser_homepage_custom_homepage_add_multiple_urls.js; "
    "browser_homepage_custom_homepage_manage_urls.js; browser_homepage_homepage.js; "
    "browser_homepage_custom_homepage_empty_state.js",
    "Setting custom URLs for new windows and new tabs, including several URLs and the empty "
    "state, each have a dedicated test.",
    [3190626],
)
C(
    69749,
    "STRONG",
    HOME + "browser_homepage_homepage_restore_defaults.js; "
    "browser_homepage_homepage_restore_defaults_2.js; browser_hometab_restore_defaults.js; "
    "browser_homepage_extension_restore_defaults.js",
    "The Restore Defaults button in the Home pane, including the extension-override case.",
    [3190627],
)
C(
    69749,
    "STRONG",
    HOME
    + "browser_homepage_firefox_home.js; browser_homepage_firefox_home_stories.js; "
    "browser_homepage_firefox_home_recent_activity.js; browser_homepage_firefox_home_widgets.js; "
    "browser_homepage_firefox_home_shortcuts.js; browser_homepage_firefox_home_firefox_logo.js; "
    "browser_homepage_firefox_home_disabled_both_off.js",
    "The Firefox Home content section is covered section by section -- stories, recent activity, "
    "widgets, shortcuts, the logo -- plus the fully-disabled state.",
    [3190769],
)
C(
    69749,
    "STRONG",
    HOME + "browser_homepage_custom_homepage_current_pages.js",
    "A test dedicated to the 'Use Current Pages' button populating the custom homepage from the "
    "open tabs.",
    [3190836],
)
C(
    69749,
    "STRONG",
    HOME
    + "browser_homepage_custom_homepage_bookmark.js; browser_homepages_use_bookmark.js",
    "Two tests cover choosing a bookmark as the homepage.",
    [3190837],
)
C(
    69749,
    "STRONG",
    HOME + "browser_homepage_firefox_home_shortcuts.js; "
    "browser_homepage_firefox_home_sponsored_shortcuts.js; "
    + NTB
    + "browser_topsites_section.js",
    "Shortcuts customisation from the settings pane, including the sponsored-shortcuts toggle.",
    [3190852],
)
C(
    69749,
    "STRONG",
    HOME + "browser_homepages_filter_aboutpreferences.js; "
    "browser_home_pane_late_group_registration.js",
    "browser_homepages_filter_aboutpreferences.js drives the settings search box and asserts the "
    "Home and Startup groups are surfaced by it.",
    [3190861],
)
C(
    69749,
    "STRONG",
    HOME + "browser_homepage_custom_homepage_manage_urls.js; "
    "browser_homepage_custom_homepage_add_multiple_urls.js",
    "The manage-URLs surface, where multiple custom pages are listed and their order changed.",
    [3311763],
)

# ================================================================ reviewed but kept
CREST(
    67503,
    "MEDIUM",
    NTU + "Widgets/Lists.test.jsx",
    "Task reordering and editing an existing task's text are not asserted -- Lists.test.jsx "
    "covers add, complete and delete, but not drag-reorder or in-place text edit.",
)
CREST(
    95385,
    "MEDIUM",
    NTU + "Widgets/Lists.test.jsx",
    "Same two gaps as suite 67503: reordering checklist items and editing an item's text.",
)
CREST(
    5403,
    "MEDIUM",
    NTB + "browser_discovery_card.js; browser_as_render.js",
    "Two groups left. The 'New Tab page - UI - US / ROW / DE / GB / CA / IE / IN / BE / CH' rows "
    "are per-region layout inspections, which depend on region-gated content the tree does not "
    "stand up. The Save to Pocket and Delete from Pocket context-menu actions need a signed-in "
    "Pocket account.",
)
