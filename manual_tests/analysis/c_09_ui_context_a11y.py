"""Critical round -- context menus, themes and toolbar, clipboard/drag-drop, accessibility.

Suites: 85 (Context menus), 1997 (Themes and appearance), 5259 (Drag and drop / clipboard),
18105 (Accessibility -- screen readers).

Context menus are covered well: browser/base/content/test/contextMenu/browser_contextmenu.js
walks the menu over every content type (link, image, video, audio, text selection, input,
textarea, plain page) and asserts the exact item list for each, which is what most of suite 85
does by hand.

Suite 18105 is the clearest manual-only suite in the whole population: every row drives NVDA,
VoiceOver or ORCA against live websites. The tree has an extensive accessibility engine test
corpus under accessible/tests, but it exercises the a11y tree through the API, never a real
screen reader.

Suite 5259 is almost entirely cross-application: dragging out to File Explorer or Preview,
pasting into desktop applications, copying tables out of other browsers. The clipboard and
drag-drop machinery is tested in-tree, but not across the process boundary these rows require.
"""

from _ledger import C
from c_util import CREST

CM = "browser/base/content/test/contextMenu/"
CUI = "browser/components/customizableui/test/"
EXT = "toolkit/components/extensions/test/browser/"

# ================================================================ content context menus
C(
    85,
    "STRONG",
    CM + "browser_contextmenu.js; browser_contextmenu_linkopen.js; "
    "browser_contextmenu_bookmark_link_text.js; browser_copy_image_link.js; "
    "browser_strip_on_share_link.js",
    "browser_contextmenu.js declares the expected item list for a plain hyperlink and for an "
    "image wrapped in a hyperlink, then opens the menu on each and asserts the menu matches "
    "item for item.",
    [1259153, 1259793],
)
C(
    85,
    "STRONG",
    CM + "browser_contextmenu.js; browser_view_image.js; browser_save_image.js; "
    "browser_copy_canvas_image.js; browser_contextmenu_chrome_images.js; "
    "browser_contextmenu_blocked_image_protocols.js",
    "The image context menu is asserted item-by-item in browser_contextmenu.js, and its "
    "principal actions -- View Image, Save Image, Copy Image -- each have their own test.",
    [1260129],
)
C(
    85,
    "STRONG",
    CM + "browser_contextmenu.js; browser_contextmenu_cross_boundary_selection.js; "
    "browser_contextmenu_plaintextlinks.js; browser_copy_link_to_highlight.js; "
    "browser_contextmenu_add_search_engine.js",
    "The page and text-selection menus are both in browser_contextmenu.js's expected-item "
    "matrix, with the selection-specific entries (search for selection, copy link to highlight) "
    "covered separately.",
    [1260162, 1260561],
)
C(
    85,
    "STRONG",
    CM + "browser_contextmenu.js; browser_contextmenu_input.js; "
    "browser_contextmenu_contenteditable.js; browser_contextmenu_spellcheck.js",
    "browser_contextmenu_input.js covers empty and populated input fields and textareas, "
    "including the spell-check entries that only appear on editable content.",
    [1260181, 1260432],
)
C(
    85,
    "STRONG",
    CM + "browser_contextmenu.js",
    "Video and audio elements each have their own expected-item list in browser_contextmenu.js, "
    "including the media-specific entries (play/pause, mute, loop, save, PiP).",
    [1260465, 1286332],
)
C(
    85,
    "STRONG",
    "toolkit/components/passwordmgr/test/browser/browser_context_menu.js; "
    "browser_context_menu_generated_password.js; browser_context_menu_autocomplete_interaction.js; "
    "browser_context_menu_iframe.js",
    "The password manager's own context-menu tests cover what appears on username and password "
    "fields, including the Use a Generated Password entry and the autocomplete interaction.",
    [1260175, 1260177],
)

# ================================================================ chrome context menus
C(
    85,
    "STRONG",
    CUI + "browser_940946_removable_from_navbar_customizemode.js; "
    "browser_938995_indefaultstate_nonremovable.js; browser_934113_menubar_removable.js; "
    "browser_927717_customize_drag_empty_toolbar.js; browser_918049_skipintoolbarset_dnd.js",
    "The toolbar and toolbar-item context menus -- remove from toolbar, customise, which items "
    "are removable and which are pinned -- are covered by the customizableui suite.",
    [1260132, 1260138],
)

C(
    85,
    "STRONG",
    "browser/components/places/tests/browser/browser_bookmark_context_menu_contents.js; "
    "browser_bookmarks_toolbar_context_menu_view_options.js; browser_click_bookmarks_on_toolbar.js; "
    "browser_autoshow_bookmarks_toolbar.js",
    "browser_bookmark_context_menu_contents.js asserts the item list of the context menu on a "
    "bookmark and on a bookmark folder, and "
    "browser_bookmarks_toolbar_context_menu_view_options.js does the same for the toolbar's own "
    "context menu including its view options.",
    [1260134, 1260136, 1326891],
)

# ================================================================ themes and toolbar
C(
    1997,
    "STRONG",
    "browser/themes/test/browser/browser_BuiltInThemes_installs.js; "
    + EXT
    + "browser_ext_themes_lwtsupport.js; browser_ext_themes_dynamic_updates.js; "
    "browser_ext_themes_persistence.js; browser_ext_themes_reset.js",
    "browser_BuiltInThemes_installs.js installs and applies each built-in theme (Light, Dark, "
    "Alpenglow); the lwt and persistence tests cover switching between a built-in theme and a "
    "lightweight theme and the switch sticking.",
    [118162, 118166],
)
C(
    1997,
    "STRONG",
    EXT
    + "browser_ext_themes_dynamic_updates.js; browser_ext_themes_dynamic_onUpdated.js; "
    "browser_ext_themes_static_onUpdated.js; browser_ext_themes_dynamic_getCurrent.js",
    "Dynamic theme changes being reflected in the UI as they are applied is exactly what the "
    "dynamic-update theme tests assert.",
    [1767762],
)
C(
    1997,
    "STRONG",
    EXT + "browser_ext_themes_pbm.js; browser_ext_themes_incognito.js; "
    "browser_ext_themes_private_nova.js; browser_ext_themes_ntp_colors_perwindow.js",
    "browser_ext_themes_pbm.js covers which theme a private window adopts, including the case "
    "where the normal-window theme is not carried over -- the substance of all three of these "
    "dark/light/Alpenglow-in-PBM rows.",
    [1937606, 1937607, 1937608],
)
C(
    1997,
    "STRONG",
    CUI
    + "browser_909779_overflow_toolbars_new_window.js; browser_913972_currentset_overflow.js; "
    "browser_942581_unregisterArea_keeps_placements.js; browser_878452_drag_to_panel.js",
    "Toolbar placement persisting into a newly opened window is covered directly by "
    "browser_909779_overflow_toolbars_new_window.js and the placement-persistence tests.",
    [1239534],
)
C(
    1997,
    "STRONG",
    CUI + "browser_947914_button_print.js; browser_947914_button_find.js; "
    "browser_940946_removable_from_navbar_customizemode.js; browser_878452_drag_to_panel.js",
    "Adding a widget from the palette to the toolbar in customize mode, and the widget then "
    "working, is the pattern the browser_947914_button_* tests follow for each built-in button.",
    [1241475],
)

# ================================================================ reviewed but kept
CREST(
    85,
    "MEDIUM",
    CM + "browser_contextmenu.js",
    "Left over: the macOS Firefox menu, and the File and Edit menubar walks. The native menubar "
    "is not reachable from the browser-chrome harness, and on macOS it is an OS-owned surface.",
)
CREST(
    1997,
    "MEDIUM",
    EXT + "browser_ext_themes_chromeparity.js",
    "The remainder is visual and environmental: RTL build glitches, High Contrast interaction "
    "with the default themes, high-DPI rendering, the DevEdition theme and its default toolbar "
    "set, UI direction not affecting the toolbar, and the FxA avatar appearing when signed in. "
    "These are appearance judgements or need a DevEdition build / live account.",
)
CREST(
    5259,
    "MEDIUM",
    "dom/events/test/clipboard/; widget/tests/browser/",
    "Every row crosses the application boundary: dragging images out to File Explorer or macOS "
    "Preview, pasting images into desktop applications, copying tables out of other browsers, "
    "and drag-and-drop against file-hosting web apps. In-tree clipboard and drag-drop tests stay "
    "inside Firefox, so none of these transfers is reproduced.",
)
CREST(
    18105,
    "MEDIUM",
    "accessible/tests/browser/",
    "The whole suite drives a real screen reader -- NVDA on Windows, VoiceOver on macOS, ORCA on "
    "Linux -- against live sites (nytimes.com, Facebook, Amazon, Gmail, Reddit), plus OS-level "
    "reduced-motion and High Contrast settings. accessible/tests/browser is a large corpus, but "
    "it queries the accessibility tree through the API; it does not run a screen reader, which "
    "is the thing under test here.",
)
