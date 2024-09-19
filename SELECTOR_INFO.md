### Selector Information
This document describes the many DOM selectors used throughout the project, in the format:
#### template
```
Selector Name: (declaration)
Selector Data: (The DOM item)
Description: (of the selector, including purpose/functionality)
Location: (of the selector in content page or Fx UI)
Path to .json: (ie, modules/data/google_search.components.json
```
#### about_addons
```
Selector Name: sidebar-options
Selector Data: "button.category[name='{name}']"
Description: Selects an option in about:addons (sidebar)
Location: Left side of about:addons page
Path to .json: modules/data/about_addons.components.json
```
```
Selector Name: theme-card
Selector Data: "div.card[aria-labelledby='{name}']"
Description: Takes the name of the intended theme to use
Location: Theme cards on about:addons page
Path to .json: modules/data/about_addons.components.json
```
#### about_config
```
Selector Name: warning-button
Selector Data: "warningButton"
Description: The button to acceot the risks of accessing about:config
Location: about:config page
Path to .json: modules/data/about_config.components.json
```
```
Selector Name: about-config-search-input
Selector Data: "about-config-search"
Description: The search input field used to find configs
Location: about:config page
Path to .json: modules/data/about_config.components.json
```
```
Selector Name: cell-edit
Selector Data: "cell-edit"
Description: The button to toggle the true/false value of a config
Location: Line item config in about:config page
Path to .json: modules/data/about_config.components.json
```
```
Selector Name: form-edit
Selector Data: "//input[@aria-label='cookiebanners.service.mode']"
Description: Text entry field when editing a str value of a config
Location: Line item config in about:config page
Path to .json: modules/data/about_config.components.json
```
#### about_downloads
```
Selector Name: no-downloads-label
Selector Data: "downloadsListEmptyDescription"
Description: Label that exists when no downloads are present
Location: about:downloads page
Path to .json: modules/data/about_downloads.components.json
```
```
Selector Name: download-target
Selector Data: "downloadTarget"
Description: Download item element
Location: In the about:downloads page when a download exists
Path to .json: modules/data/about_downloads.components.json
```
#### about_downloads_context_menu
```
Selector Name: downloads-panel
Selector Data: "downloadsPanel"
Description: Downloads panel identifier
Location: Downloads toolbar button
Path to .json: modules/data/about_downloads_context_menu.components.json
```
```
Selector Name: menu-root
Selector Data: "downloadsContextMenu"
Description: Downloads context menu root
Location: Context click an item in downloads list
Path to .json: modules/data/about_downloads_context_menu.components.json
```
```
Selector Name: open-in-system-viewer
Selector Data: "downloadUseSystemDefaultMenuItem"
Description: Downloads context menu option
Location: Downloaded file context menu
Path to .json: modules/data/about_downloads_context_menu.components.json
```
```
Selector Name: always-open-in-system-viewer
Selector Data: "downloadAlwaysUseSystemDefaultMenuItem"
Description: Downloads context menu option "Always Open Similar Files"
Location: Downloaded file context menu
Path to .json: modules/data/about_downloads_context_menu.components.json
```
```
Selector Name: show-in-file-browser
Selector Data: "downloadShowMenuItem"
Description: Downloads context menu option "Show in Finder"
Location: Downloaded file context menu
Path to .json: modules/data/about_downloads_context_menu.components.json
```
```
Selector Name: go-to-download-page
Selector Data: "downloadOpenReferrerMenuItem"
Description: Downloads context menu option "Go to Download Page"
Location: Downloaded file context menu
Path to .json: modules/data/about_downloads_context_menu.components.json
```
```
Selector Name: copy-download-link
Selector Data: "downloadCopyLocationMenuItem"
Description: Downloads context menu option "Copy Download Link"
Location: Downloaded file context menu
Path to .json: modules/data/about_downloads_context_menu.components.json
```
```
Selector Name: delete
Selector Data: downloadDeleteFileMenuItem
Description: Downloads context menu option "Delete"
Location: Downloaded file context menu
Path to .json: modules/data/about_downloads_context_menu.components.json
```
```
Selector Name: remove-from-history
Selector Data: "downloadRemoveFromHistoryMenuItem"
Description: Downloads context menu option "Remove From History"
Location: Downloaded file context menu
Path to .json: modules/data/about_downloads_context_menu.components.json
```
```
Selector Name: clear-downloads
Selector Data: "menuitem[data-l10n-id='downloads-cmd-clear-downloads']"
Description: Downloads context menu option "Clear Preview Panel"
Location: Downloaded file context menu
Path to .json: modules/data/about_downloads_context_menu.components.json
```
#### about_glean
```
Selector Name: ping-id-input
Selector Data: "tag-pings"
Description: Text entry field to set a memorable tag for the ping
Location: Line 1 of the about:glean page's 'About testing' process
Path to .json: modules/data/about_glean.components.json
```
```
Selector Name: ping-submit-button
Selector Data: "controls-submit"
Description: 'Apply settings and submit ping' button
Location: Line 4 of the about:glean page's 'About testing' process
Path to .json: modules/data/about_glean.components.json
```
```
Selector Name: ping-submit-label
Selector Data: "label[for='controls-submit']"
Description: Text updated dynamically to reflect change in ping ID
Location: Line 4 of the about:glean page's 'About testing' process
Path to .json: modules/data/about_glean.components.json
```
#### context_menu
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
#### google_search
```
Selector Name: search-bar-textarea
Selector Data: "textarea[aria-label='Search']"
Description: Text entry area of the search field
Location: google.com content page
Path to .json: modules/data/google_search.components.json
```
#### login_autofill
```
Selector name: input-field
Selector Data: input[autocomplete='{name}']
Description: Input field
Location: Input field in the autofill demo page
Path to .json: modules/data/login_autofill.components.json
```
```
Selector name: username-field
Selector Data: input[placeholder='username']
Description: Username field
Location: Username field in the autofill demo page
Path to .json: modules/data/login_autofill.components.json
```
```
Selector name: submit-form
Selector Data: input[value='Log In']
Description: Login button in the submit form
Location: Login button in the autofill demo page
Path to .json: modules/data/login_autofill.components.json
```
```
Selector name: save-login-popup
Selector Data: notification-popup
Description: Save login doorhanger
Location: Save login doorhanger under the URL bar
Path to .json: modules/data/login_autofill.components.json
```
```
Selector name: username-login-field
Selector Data: /html/body/div[1]/form[2]/input[1]
Description: Username login field
Location: Username field in the login demo page
Path to .json: modules/data/login_autofill.components.json
```
```
Selector name: password-login-field
Selector Data: /html/body/div[1]/form[2]/input[2]
Description: Password login field
Location: Password field in the login demo page
Path to .json: modules/data/login_autofill.components.json
```
```
Selector name: submit-button-login
Selector Data: /html/body/div[1]/form[2]/input[3]
Description: Login submit button
Location: Submit button in the login demo page 
Path to .json: modules/data/login_autofill.components.json
```
#### navigation
```
Selector name: awesome-bar
Selector Data: urlbar-input
Description: Awesome bar / URL bar
Location: Any clickable area on the awesome bar
Path to .json: modules/data/navigation.components.json
```
```
Selector name: results-dropdown
Selector Data: urlbar-results
Description: URL bar search results
Location: Any search result item from the URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: tab-to-search-text-span
Selector Data: urlbarView-dynamic-onboardTabToSearch-text-container
Description: Tab to search text span
Location: URL bar
Path to .json: modules/data/navigation.components.json
```
```
Selector name: search-mode-span
Selector Data: urlbar-search-mode-indicator-title
Description: Search mode span
Location: URL bar
Path to .json: modules/data/navigation.components.json
```
```
Selector name: overflow-item
Selector Data: [class='urlbarView-title urlbarView-overflowable']
Description: The title of every search result from the URL bar search results
Location: Any search result title item from the URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: search-one-off-settings-button
Selector Data: urlbar-anon-search-settings
Description: Search settings button
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: quick-actions-refresh-button
Selector Data: urlbarView-row-3-label-0
Description: Quick action refresh button
Location: URL bar
Path to .json: modules/data/navigation.components.json
```
```
Selector name: refresh-intervention-card
Selector Data: div[tip-type='intervention_refresh']
Description: 
Location:
Path to .json: modules/data/navigation.components.json
```
```
Selector name: fx-refresh-text
Selector Data: span[data-l10n-id='intervention-refresh-profile']
Description: Refresh Firefox button text
Location: URL bar results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: fx-refresh-button
Selector Data: span[role='button'][data-l10n-id='intervention-refresh-profile-confirm']
Description: Refresh Firefox button
Location: URL bar results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: fx-refresh-menu
Selector Data: span[data-l10n-id='urlbar-result-menu-button'][title='Open menu']
Description: Trending menu search results
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: fx-refresh-menu-get-help-item
Selector Data: menuitem[data-l10n-id='urlbar-result-menu-tip-get-help']
Description: Trending search results menu item
Location: Menu items for the trending results in the URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: fx-refresh-menu-get-help-item-get-help
Selector Data: urlbarView-result-menuitem
Description: Trending search results menu item
Location: Menu items for the trending results in the URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: search-engine-suggestion-row
Selector Data: div[class='urlbarView-row'][type='search_engine']
Description: Search suggestions from the URL bar search results
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: search-one-off-browser-button
Selector Data: urlbar-engine-one-off-item-{source}
Description: search one off buttons
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: panel-ui-button
Selector Data: PanelUI-button
Description: Panel UI button / hamburger menu
Location: Far right in the toolbar
Path to .json: modules/data/navigation.components.json
```
```
Selector name: navigation-background-component
Selector Data: nav-bar
Description: Navigation bar
Location: Any area on the navigation bar
Path to .json: modules/data/navigation.components.json
```
```
Selector name: context-menu-paste-and-go
Selector Data: paste-and-go
Description: Any search bar context menu option "paste-and-go" 
Location: Any search bar
Path to .json: modules/data/navigation.components.json
```
```
Selector name: private-browsing-icon
Selector Data: private-browsing-indicator-icon
Description: Private browsing icon
Location: Private browsing mode
Path to .json: modules/data/navigation.components.json
```
```
Selector name: add-extra-search-engine
Selector Data: [id*=urlbar-engine-one-off-item-engine--1][tooltiptext*='{0}']
Description: Add extra search engine in the url bar
Location: URL bar
Path to .json: modules/data/navigation.components.json
```
```
Selector name: search-one-off-engine-button
Selector Data: [id*=urlbar-engine-one-off-item-engine][tooltiptext^='{0}']
Description: Search one off engine button
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: downloads-button
Selector Data: downloads-button
Description: Toolbar download button
Location: Toolbar after downloading a file
Path to .json: modules/data/navigation.components.json
```
```
Selector name: search-results-container
Selector Data: urlbar-results
Description: URL bar search results
Location: Any search result item from the URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: addon-suggestion
Selector Data: div.urlbarView-row[type='rust_amo'] span.urlbarView-title.urlbarView-overflowable
Description: Addon suggestion in the URL bar search results
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: search-suggestion-list
Selector Data: div.urlbarView-row[type='search_engine'] span.urlbarView-title
Description: Search suggestion list
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: sponsored-suggestion
Selector Data: urlbarView-row-body-description
Description: Sponsored search results
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: firefox-suggest
Selector Data: div.urlbarView-row[label='Firefox Suggest'] > span.urlbarView-row-inner
Description: Firefox suggestion search results
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: search-result-autofill-adaptive-element
Selector Data: .//*[@type='autofill_adaptive']
Description: Search result autofill adaptive element
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: search-result
Selector Data: //div[@data-text-ad]//a
Description: ad search results
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: shield-icon
Selector Data: tracking-protection-icon-container
Description: Shield icon
Location: URL bar / Awseome bar after visiting a website
Path to .json: modules/data/navigation.components.json
```
```
Selector name: cryptominers
Selector Data: .protections-popup-category.subviewbutton.subviewbutton-iconic.subviewbutton-nav.blocked
Description: Cryptominer trackers
Location: Shield icon
Path to .json: modules/data/navigation.components.json
```
```
Selector name: no-trackers-detected
Selector Data: protections-popup-no-trackers-found-description
Description: No trackers detected
Location: Click on the shield icon
Path to .json: modules/data/navigation.components.json
```
```
Selector name: lock-icon
Selector Data: identity-icon
Description: Site information panel (Lock icon)
Location: URL bar / Awseome bar after visiting a website
Path to .json: modules/data/navigation.components.json
```
```
Selector name: connection-secure-button
Selector Data: identity-popup-security-button
Description: Connection secure button
Location: In the site information panel (lock icon)
Path to .json: modules/data/navigation.components.json
```
```
Selector name: more-information-button
Selector Data: identity-popup-more-info
Description: More information button in the connection security panel
Location: In the connection security insde the site information panel (lock icon)
Path to .json: modules/data/navigation.components.json
```
```
Selector name: search-result-url
Selector Data: .urlbarView-title.urlbarView-overflowable[is-url='']
Description: Search results url
Location: URL bar / Awesome bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: search-result-action-term
Selector Data: .urlbarView-action
Description: Search results entries
Location: URL bar / Awesome bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector name: refresh-button
Selector Data: reload-button
Description: Reload current page
Location: Toolbar
Path to .json: modules/data/navigation.components.json
```
```
Selector name: known-fingerprints
Selector Data: .protections-popup-category.subviewbutton.subviewbutton-iconic.blocked.subviewbutton-nav
Description: Known fingerprints
Location: Shield icon
Path to .json: modules/data/navigation.components.json
```
```
Selector name: fingerprints-blocked-subpanel
Selector Data: protections-popup-fingerprintersView
Description: Fingerprints subpanel
Location: Inside the shield incon in fingerprints subpanel
Path to .json: modules/data/navigation.components.json
```
```
Selector name: star-button
Selector Data: star-button-box
Description: Star button to bookmark a page
Location: URL bar
Path to .json: modules/data/navigation.components.json
```
```
Selector name: save-bookmark-button
Selector Data: editBookmarkPanelDoneButton
Description: Save bookmark
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector name: blue-star-button
Selector Data: image[id='star-button'][starred='true']
Description: Bookmarked page
Location: URL bar
Path to .json: modules/data/navigation.components.json
```
```
Selector name: download-panel-item
Selector Data: vbox[class='downloadContainer']
Description: Downloaded item in the download panel
Location: Download panel
Path to .json: modules/data/navigation.components.json
```
```
Selector name: edit-bookmark-panel
Selector Data: editBMPanel_namePicker
Description: Edit bookmark panel
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector name: remove-bookmark-button
Selector Data: editBookmarkPanelRemoveButton
Description: Remove bookmark button
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector name: forget-button
Selector Data: panic-button
Description: Forget button
Location: Toolbar after adding it from customize
Path to .json: modules/data/navigation.components.json
```
```
Selector name: history-button
Selector Data: history-panelmenu
Description: History button
Location: Toolbar after adding it from customize
Path to .json: modules/data/navigation.components.json
```
```
Selector name: library-button
Selector Data: library-button
Description: Library button
Location: Toolbar after adding it from customize
Path to .json: modules/data/navigation.components.json
```
```
Selector name: library-history-submenu-button
Selector Data: appMenu-library-history-button
Description: Library history submenu button
Location: Inside the library button in the toolbar
Path to .json: modules/data/navigation.components.json
```
```
Selector name: bookmarks-type-dropdown
Selector Data: editBMPanel_folderMenuList
Description: Bookmark location
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector name: bookmarks-type-dropdown-other
Selector Data: editBMPanel_unfiledRootItem
Description: Bookmark location - Other bookmarks
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector name: other-bookmarks
Selector Data: OtherBookmarks
Description: Other bookmarks option
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector name: other-bookmarks-popup
Selector Data: OtherBookmarksPopup
Description: Other bookmarks submenu
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector name: new-bookmark-name-field
Selector Data: editBMPanel_namePicker
Description: New bookmark name field
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector name: new-bookmark-url-field
Selector Data: editBMPanel_locationField
Description: New bookmark url field
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector name: new-bookmark-tags-field
Selector Data: editBMPanel_tagsField
Description: New bookmark tags field
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector name: new-bookmark-keyword-field
Selector Data: editBMPanel_keywordField
Description: New bookmark keyword field
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector name: bookmark-dialog
Selector Data: ookmarkpropertiesdialog
Description: Bookmark dialog
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector name: bookmark-accept-button
Selector Data: button[dlgtype='accept']
Description: Bookmark accept button
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector name: bookmark-iframe
Selector Data: browser[class='dialogFrame']
Description: Add bookmark advanced
Location: Add bookmark from bookmarks sidebar
Path to .json: modules/data/navigation.components.json
```
```
Selector name: bookmark-robots
Selector Data: menuitem[label='Robots 2']
Description: A bookmark named robots
Location: A bookmark in other bookmarks
Path to .json: modules/data/navigation.components.json
```
```
Selector name: bookmark-current-tab
Selector Data: panelMenuBookmarkThisPage
Description: Bookmark current tab button
Location: Menu button / hamburger menu
Path to .json: modules/data/navigation.components.json
```