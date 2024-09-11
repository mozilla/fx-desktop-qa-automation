### Selector Information
This document describes the many DOM selectors used throughout the project, in the format:

```
Selector Name: (declaration)
Selector Data: (The DOM item)
Description: (of the selector, including purpose/functionality)
Location: (of the selector in content page or Fx UI)
Path to .json: (ie, modules/data/google_search.components.json
```
```
Selector Name: search-bar-textarea
Selector Data: "textarea[aria-label='Search']"
Description: Text entry area of the search field
Location: google.com content page
Path to .json: modules/data/google_search.components.json
```
```
Selector Name: context-menu-search-selected-text
Selector Data: "context-searchselect"
Description: Selected text context menu option "Search Google for <selected text>"
Location: Any content page user selected text
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-take-screenshot
Selector Data: "context-take-screenshot"
Description: Page context menu option "Take Screenshot"
Location: Any non-linked content space
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-save-page-as
Selector Data: "context-savepage"
Description: Page context menu option "Save Page As…"
Location: Any non-linked content space
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-always-open-similar-files
Selector Data: "downloadAlwaysOpenSimilarFilesMenuItem"
Description: Downloads context click option "Always Open Similar Files"
Location: Any downloaded item in the Downloads panel
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: customize-firefox-add-toolbar
Selector Data: "customize-context-addToToolbar"
Description: Customize window context click option "Add to Toolbar"
Location: Any item in the customize Firefox content
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-add-bookmark
Selector Data: "placesContext_new:bookmark"
Description: Bookmarks Toolbar context click option "Add Bookmark…"
Location: Any clickable area on the Bookmarks Toolbar
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-delete-page
Selector Data: "placesContext_delete_history"
Description: Hamburger history submenu context click option "Delete Page"
Location: Any history item in the Hamburger history list
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-pin-tab
Selector Data: "context_pinTab"
Description: Tab context click option "Pin Tab"
Location: Any unpinned browser tab
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-unpin-tab
Selector Data: "context_unpinTab"
Description: Tab context click option "Unpin Tab"
Location: Any pinned browser tab
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-reopen-tab
Selector Data: "context_undoCloseTab"
Description: Tab context click option "Reopen Closed Tab"
Location: Any clickable place on the tabbar (after a tab has been closed)
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-duplicate-tab
Selector Data: "context_duplicateTab"
Description: Tab context click option "Duplicate Tab"
Location: Any tab
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-close-multiple-tabs
Selector Data: "context_closeTabOptions"
Description: Tab context click option "Close Multiple Tabs"
Location: Any tab (active when multiple nonpinned tabs are open)
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-close-multiple-tabs-to-right
Selector Data: "context_closeTabsToTheEnd"
Description: Close Multiple Tabs sub-option "Close Tabs to Right"
Location: Any tab (active when nonpinned tabs are open to the right of clicked tab)
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-close-multiple-tabs-other-tabs
Selector Data: "context_closeOtherTabs"
Description: Close Multiple Tabs sub-option "Close Other Tabs"
Location: Any tab (active when multiple nonpinned tabs are open)
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-close-multiple-tabs-to-left
Selector Data: "context_closeTabsToTheStart"
Description: Close Multiple Tabs sub-option "Close Tabs to Right"
Location: Any tab (active when nonpinned tabs are open to the right of clicked tab)
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-close-tab
Selector Data: "context_closeTab"
Description: Tab context click option "Close Tab"
Location: Any tab
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-open-link-in-tab
Selector Data: "context-openlinkintab"
Description: Link context menu option "Open Link in New Tab"
Location: Any content url link
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-open-link-in-new-window
Selector Data: "context-openlink"
Description: Link context menu option "Open Link in New Window"
Location: Any content url link
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-open-link-in-new-private-window
Selector Data: "context-openlinkprivate"
Description: Link context menu option "Open Link in New Private Window"
Location: Any content url link
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-save-link
Selector Data: "context-savelink"
Description: Link context menu option "Save Link As…"
Location: Any content url link
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-copy-link
Selector Data: "context-copylink"
Description: Link context menu option "Copy Link"
Location: Any content url link
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-inspect
Selector Data: "context-inspect"
Description: Link context menu option "Inspect"
Location: Any content url link
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-open-image-in-new-tab
Selector Data: "context-viewimage"
Description: Image context menu option "Open Image in New Tab"
Location: Any content page image
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-save-image-as
Selector Data: "context-saveimage"
Description: Image context menu option "Save Image As…"
Location: Any content page image
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-copy-image-link
Selector Data: "context-copyimage"
Description: Image context menu option "Copy Image"
Location: Any content page image
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-copy
Selector Data: "context-copy"
Description: Page content context menu option "Copy"
Location: Any selected context text
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-paste
Selector Data: "context-paste"
Description: Context menu option "Paste"
Location: Any text field cntext ment
Path to .json: modules/data/context_menu.components.json
```
