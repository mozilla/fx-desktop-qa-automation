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
#### about_logins
```
Selector Name: login-count
Selector Data: "count"
Description: The number of passwords saved/is diplayed
Location: Top left of the about:logins page, under the add button
Path to .json: modules/data/about_logins.components.json
```
```
Selector Name: login-list-item
Selector Data: "list-item"
Description: All the saved login items, includes a hidden placeholder
Location: Left side of the about:logins page
Path to .json: modules/data/about_logins.components.json
```
```
Selector Name: login-list
Selector Data: "login-list"
Description: The list box containing the list of saved logins (is a shadow parent)
Location: The about:login's page's sidebar
Path to .json: modules/data/about_logins.components.json
```
```
Selector Name: create-login-button
Selector Data: "create-login-button"
Description: The add password (+) button
Location: The about:login's page's sidebar
Path to .json: modules/data/about_logins.components.json
```
```
Selector Name: login-filter
Selector Data: "login-filter"
Description: The Search passwords text input field (is a shadow parent)
Location: The about:login's page's sidebar
Path to .json: modules/data/about_logins.components.json
```
```
Selector Name: login-filter-input
Selector Data: "filter"
Description: The Search passwords text input field
Location: The about:login's page's sidebar
Path to .json: modules/data/about_logins.components.json
```
```
Selector Name: login-item
Selector Data: "login-item"
Description: Individual saved login item (is a shadow parent)
Location: The about:login's page's sidebar
Path to .json: modules/data/about_logins.components.json
```
```
Selector Name: login-item-type
Selector Data: "{name}"
Description: Individual saved login item
Location: The about:login's page's sidebar
Path to .json: modules/data/about_logins.components.json
```
```
Selector Name: form-actions-row
Selector Data: "form-actions-row"
Description: New login page's Cancel and Save button container (is a shadow parent)
Location: The about:login's new login page
Path to .json: modules/data/about_logins.components.json
```
```
Selector Name: save-changes-button
Selector Data: "save-changes-button"
Description: New login page's Save button
Location: The about:login's new login page
Path to .json: modules/data/about_logins.components.json
```
```
Selector Name: website-address
Selector Data: ".origin-input"
Description: The website address row
Location: The about:login's main login page
Path to .json: modules/data/about_logins.components.json
```
```
Selector Name: about-logins-page-username-field
Selector Data: ".detail-row input[name='username']"
Description: The Username field
Location: The about:login's main login page
Path to .json: modules/data/about_logins.components.json
```
```
Selector Name: about-logins-page-password-field
Selector Data: ".detail-row .reveal-password-wrapper input.password-display, .detail-row .reveal-password-wrapper input[name='password']"
Description: The Password field
Location: The about:login's main login page
Path to .json: modules/data/about_logins.components.json
```
#### about_newtab
```
Selector Name: incontent-search-input
Selector Data: "fake-editable"
Description: The in page search input field
Location: The about:newtab page
Path to .json: modules/data/about_newtab.components.json
```
```
Selector Name: card-by-index
Selector Data: "article-ds-card"
Description: Tile/card by index
Location: The about:newtab page
Path to .json: modules/data/about_newtab.components.json
```
```
Selector Name: loaded-image-by-index
Selector Data: "article.ds-card:nth-child({index}) > div.img-wrapper > picture.loaded"
Description: Tile image by index
Location: The about:newtab page
Path to .json: modules/data/about_newtab.components.json
```
```
Selector Name: sponsored-site-card
Selector Data: "top-site-outer"
Description: Space containing sponsored site card
Location: The about:newtab page
Path to .json: modules/data/about_newtab.components.json
```
```
Selector Name: top-site-image-by-index
Selector Data: ".top-sites-list li:nth-of-type({index}) .top-site-icon.rich-icon"
Description: Sponsored site card image by index
Location: The about:newtab page
Path to .json: modules/data/about_newtab.components.json
```
```
Selector Name: sponsored-site-card-menu-button
Selector Data: "button[class='context-menu-button icon']"
Description: Sponsored site card open menu button (…)
Location: The about:newtab page
Path to .json: modules/data/about_newtab.components.json
```
```
Selector Name: top-sites-list
Selector Data: "top-sites-list"
Description: Element containing all of the Top site cards
Location: The about:newtab page
Path to .json: modules/data/about_newtab.components.json
```
```
Selector Name: recommended-by-pocket-list
Selector Data: "ds-card-grid-include-descriptions"
Description: Element containing all of the recommended site cards
Location: The about:newtab page
Path to .json: modules/data/about_newtab.components.json
```
```
Selector Name: story-sponsored-footer
Selector Data: "article.ds-card > div > div > p.story-sponsored-label"
Description: Element containing all of the Sponsored site cards
Location: The about:newtab page
Path to .json: modules/data/about_newtab.components.json
```
```
Selector Name: popular-topics-list
Selector Data: ".ds-navigation > ul"
Description: Element containing all of the Popular Topics cards
Location: The about:newtab page
Path to .json: modules/data/about_newtab.components.json
```
```
Selector Name: recent-activity-section
Selector Data: "discovery-stream"
Description: recent Activity section header
Location: The about:newtab page
Path to .json: modules/data/about_newtab.components.json
```
```
Selector Name: recent-activity-list
Selector Data: "//div[following-sibling::div[@class='section-top-bar']]"
Description: Element containing all of the Recent Activity cards
Location: The about:newtab page
Path to .json: modules/data/about_newtab.components.json
```
```
Selector Name: sponsored-site-context-menu-list
Selector Data: "ul[class=\"context-menu-list\"]"
Description: A Sponsored tile context menu options list
Location: The about:newtab page via Sponsored tile Open Menu button (…)
Path to .json: modules/data/about_newtab.components.json
```
```
Selector Name: body-logo
Selector Data: "logo"
Description: The Firefox logo
Location: The about:newtab page
Path to .json: modules/data/about_newtab.components.json
```
#### about_prefs
```
Selector Name: search-engine-dropdown-root
Selector Data: defaultEngine
Description: The element containing the search engine options list (is a shadow root)
Location: about:preferences#search
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: search-engine-dropmarker
Selector Data: "dropmarker"
Description: Button that opens the search engine options list
Location: about:preferences#search
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: find-in-settings
Selector Data: "searchInput"
Description: Find in Settings input field (is a shadow root)
Location: about:preferences
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: find-in-settings-input
Selector Data: "input[placeholder='Find in Settings']"
Description: Find in Settings input field
Location: about:preferences
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: h2-enhanced-tracking-protection
Selector Data: h2[data-l10n-id='content-blocking-enhanced-tracking-protection']"
Description: Enhance Tracking Protection sub-header
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: save-and-fill-addresses
Selector Data: "checkbox[label='Save and fill addresses']"
Description: Label for Autofill > Save and fill addresses option
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: save-and-fill-payment-methods
Selector Data: "checkbox[label='Save and fill payment methods']"
Description: Label for Autofill > Save and fill payment methods option
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: prefs-button
Selector Data: "button[label^='{name}']"
Description: Checkbox for a option by label
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: import-browser-data
Selector Data: "button[id='data-migration']"
Description: Import Browser Data > Import Data button
Location: about:preferences#general
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: migration-popup
Selector Data: "button[id='data-migration']"
Description: Import Browser Data popup (is a shadow root)
Location: about:preferences#general as result of Import Data button click
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: migration-import-button
Selector Data: "button.primary.migration-import-button"
Description: Import data popup Import button
Location: about:preferences#general as result of Import Data button click
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: migration-progress-header
Selector Data: "h1#progress-header"
Description: Import data popup progress
Location: about:preferences#general as result of Import Data button click
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: cc-saved-options
Selector Data: "option[data-l10n-id='credit-card-label-number-name-expiration-2']"
Description: The "Add card" modal, containing 4 fields
Location: Inside the "Add card" form in the Saved payment methods section on the about:preferences#privacy page
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: panel-popup-button
Selector Data: "button[data-l10n-id='{name}']"
Description: Element for a button by label
Location: about:preferences#privacy popup dialog for adding a new address profile
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: browser-popup
Selector Data: "dialogFrame"
Description: The webelement for the iframe that commonly appears
Location: about:preferences#privacy popup dialog
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: saved-addresses
Selector Data: "addresses"
Description: The element that contains the saved addresses
Location: about:preferences#privacy Saved Addresses popup dialog
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: saved-addresses-values
Selector Data: "#addresses option"
Description: The element that contains the saved address values
Location: about:preferences#privacy Saved Addresses popup dialog
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: panel-popup-stack
Selector Data: "dialogStack"
Description: The element that contains the credit card profile values
Location: about:preferences#privacy Saved payment methods popup dialog
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: show-suggestions
Selector Data: "checkbox[data-l10n-id='search-show-suggestions-option']"
Description: The Show search suggestions check-box
Location: about:preferences#search
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: firefox-suggest-nonsponsored
Selector Data: "firefoxSuggestNonsponsored"
Description: The Suggestions from Firefox check-box
Location: about:preferences#search > Address Bar - Firefox Suggest
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: firefox-suggest-sponsored
Selector Data: "firefoxSuggestSponsored"
Description: The Suggestions from sponsors check-box
Location: about:preferences#search > Address Bar - Firefox Suggest
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: prefs-html-root
Selector Data: "preferences-root"
Description: The html root element of about:prefs pages
Location: about:preferences
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: home-new-tabs-dropdown
Selector Data: "newTabMode"
Description: The expander for "New tabs" menu
Location: about:preferences#home
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: home-new-window-dropdown
Selector Data: "homeMode"
Description: The expander for "Homepage and new windows" menu
Location: about:preferences#home
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: home-new-tabs-dropdown-option-default
Selector Data: "menuitem[data-l10n-id=\"home-mode-choice-default-fx\"]"
Description: The default option for New tabs menu
Location: about:preferences#home
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: custom-radio
Selector Data: "customRadio"
Description: In Enhanced Tracking Protection, the Custom radio button
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: cookies-checkbox
Selector Data: "contentBlockingBlockCookiesCheckbox"
Description: In Enhanced Tracking Protection, the check-box for Cookies
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: cookies-isolate-social-media-option
Selector Data: "isolateCookiesSocialMedia"
Description: In Enhanced Tracking Protection, the option for Cookies…, and isolate other…
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: tracking-in-all-windows
Selector Data: "menuitem[data-l10n-id='content-blocking-tracking-protection-option-all-windows']"
Description: In Enhanced Tracking Protection, the option for Tracking content, In all windows
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: tracking-checkbox
Selector Data: "contentBlockingTrackingProtectionCheckbox"
Description: In Enhanced Tracking Protection, the check-box for Tracking content
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: cryptominers-checkbox
Selector Data: "contentBlockingCryptominersCheckbox"
Description: In Enhanced Tracking Protection, the check-box for Cryptominers
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: known-fingerprints-checkbox
Selector Data: "contentBlockingFingerprintingCheckbox"
Description: In Enhanced Tracking Protection, the check-box for Known fingerprinters
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: suspected-fingerprints-checkbox
Selector Data: "contentBlockingFingerprintingProtectionCheckbox"
Description: In Enhanced Tracking Protection, the check-box for Suspected fingerprinters
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: cookies-shadow-root
Selector Data: "dialog[buttons='accept,cancel']"
Description: The Manage Cookies and Site Data dialog root (is a shadow root)
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: cookies-manage-data
Selector Data: "siteDataSettings"
Description: In Cookies and Site data, the Manage Data… button
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: cookies-manage-data-sitelist
Selector Data: "sitesList"
Description: The list of stored cookies in Manage Cookies and Site Data dialog
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: manage-cookies-site
Selector Data: "richlistitem[host='{name}']"
Description: Cookie item in Manage Cookies and Site Data dialog
Location: about:preferences#privacy Cookies and Site Data subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: remove-selected-cookie-button
Selector Data: "removeSelected"
Description: In Manage Cookie and Site Data dialog when a cookie item is selected
Location: about:preferences#privacy Cookies and Site Data subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: remove-all-button
Selector Data: "removeAll"
Description: In Manage Cookie and Site Data dialog
Location: about:preferences#privacy Cookies and Site Data subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: notifications-allow-button
Selector Data: "button[class='popup-notification-primary-button primary footer-button']"
Description: Notification popup Allow button
Location:
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: notifications-block-button
Selector Data: "button[class='popup-notification-secondary-button footer-button']"
Description: Notification popup Block button
Location:
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: notifications-block-button
Selector Data: "button[class='popup-notification-secondary-button footer-button']"
Description: Notification popup Block button
Location:
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: clear-data-dialog-options
Selector Data: "hbox.checkbox-label-box"
Description: The element containing the clear data dialog options
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: clear-data-accept-button
Selector Data: "[class='button-text'][value='Clear']"
Description: The clear data dialog Clear button
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: manage-data-save-changes-button
Selector Data: "[class='button-text'][value='Save Changes']"
Description: The manage data dialog Save Changes button
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: permissions-notifications-button
Selector Data: "notificationSettingsButton"
Description: Permissions > Notifications > Settings… button
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: permissions-notifications-popup-websites
Selector Data: "permissionsBox"
Description: Notifications Permissions site list
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: permissions-notifications-popup-websites-item
Selector Data: "richlistitem[origin='{name}']"
Description: Notifications Permissions site by name
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: permissions-notifications-popup-websites-item-status
Selector Data: "website-status"
Description: Notifications Permissions site status
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: update_available_button
Selector Data: "updateButton"
Description: Firefox Updates > Update available button
Location: about:preferences#general
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: up_to_date_button
Selector Data: "checkForUpdatesButton3"
Description: Firefox Updates > Check for updates button
Location: about:preferences#general
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: cookies-privacy-label
Selector Data: "description[data-l10n-id='sitedata-delete-on-close-private-browsing2']"
Description: Message in Cookies and Site data when History is not remembered
Location: about:preferences#privacy
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: cookies-delete-on-close
Selector Data: "deleteOnClose"
Description: Check box for Delete cookies and site data when Firefox is closed
Location: about:preferences#privacy Cookies and Site Data subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: logins-ask-to-save-password
Selector Data: "savePasswords"
Description: Check box for Ask to save passwords
Location: about:preferences#privacy Passwords subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: logins-exceptions
Selector Data: "passwordExceptions"
Description: Manage Exceptions… button
Location: about:preferences#privacy Passwords subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: history-privacy-label
Selector Data: "description[data-l10n-id='history-dontremember-description']"
Description: Message History is not remembered
Location: about:preferences#privacy History subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: language-dropdown
Selector Data: "primaryBrowserLocale"
Description: Language local menu list
Location: about:preferences#general Language subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: language-set-alternative-button
Selector Data: "[data-l10n-id='manage-browser-languages-button']"
Description: Set Alternatives… button
Location: about:preferences#general Language subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: language-settings-dialog
Selector Data: "BrowserLanguagesDialog"
Description: The Language Set Alternatives dialog
Location: about:preferences#general Language subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: language-settings-select
Selector Data: "[data-l10n-id='browser-languages-select-language']"
Description: In the Language Set Alternatives dialog, the Select a language to add button
Location: about:preferences#general Language subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: language-settings-search
Selector Data: "menuitem[value='search']"
Description: In the Language Set Alternatives dialog, the Select a language to add, Search for more languages… option
Location: about:preferences#general Language subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: language-option-by-code
Selector Data: "menuitem[value='{}']"
Description: In the Language Set Alternatives dialog, Select a language by language code
Location: about:preferences#general Language subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: language-added-list
Selector Data: "selectedLocales"
Description: In the Language Set Alternatives dialog, List of added languages
Location: about:preferences#general Language subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: language-settings-add-button
Selector Data: "button[data-l10n-id='languages-customize-add']"
Description: In the Language Set Alternatives dialog, Add button
Location: about:preferences#general Language subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: language-settings-ok
Selector Data: "button[dlgtype='accept']"
Description: In the Language Set Alternatives dialog, OK button
Location: about:preferences#general Language subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: history_menulist
Selector Data: "historyMode"
Description: Menu for "Firefox will" option
Location: about:preferences#privacy History subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: mime-type-item
Selector Data: "richlistitem[type='{item}']"
Description: Content type option by item
Location: about:preferences#general Applications subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: mime-type-item-description
Selector Data: "label[data-l10n-id='applications-use-app-default-label']"
Description: Content type option default label
Location: about:preferences#general Applications subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: pdf-content-type
Selector Data: "//*[local-name()='hbox' and @class='typeContainer']//*[local-name()='label' and @class='typeDescription' and text()='Portable Document Format (PDF)']",
Description: PDF content type option
Location: about:preferences#general Applications subsection
Path to .json: modules/data/about_prefs.components.json
```
```
Selector Name: pdf-actions-menu
Selector Data: "richlistitem[type='application/pdf'] menulist.actionsMenu"
Description: PDF content type options list
Location: about:preferences#general Applications subsection
Path to .json: modules/data/about_prefs.components.json
```
#### about_profiles
```
Selector Name: profile-container
Selector Data: "profiles"
Description: Element containing list of all profiles
Location: about:profiles
Path to .json: modules/data/about_profiles.components.json
```
```
Selector Name: profile-container-item-default-header
Selector Data: "ph3[data-l10n-id='profiles-in-use-profile']"
Description: Element containing the default in use profile
Location: about:profiles
Path to .json: modules/data/about_profiles.components.json
```
```
Selector Name: profile-container-item-profile-name
Selector Data: "h2[data-l10n-id='profiles-name']"
Description: Element containing the profile name
Location: about:profiles
Path to .json: modules/data/about_profiles.components.json
```
```
Selector Name: profile-container-item-button
Selector Data: "button[data-l10n-id='{name}']"
Description: Element containing the option buttons for the profile
Location: about:profiles
Path to .json: modules/data/about_profiles.components.json
```
```
Selector Name: profile-container-item-table-row-value
Selector Data: "td"
Description: Element containing the profile table row values
Location: about:profiles
Path to .json: modules/data/about_profiles.components.json
```
```
Selector Name: profile-container-item-table-row
Selector Data: "tr"
Description: Element containing the profile table row
Location: about:profiles
Path to .json: modules/data/about_profiles.components.json
```
#### about_telemetry
```
Selector Name: category-raw
Selector Data: "category-raw"
Description: Raw JSON option
Location: about:telemetry Sidebar option
Path to .json: modules/data/about_telemetry.components.json
```
```
Selector Name: rawdata-tab
Selector Data: "//li[@class='tabs-menu-item rawdata ']//a[@id='rawdata-tab']"
Description: Raw Data tab
Location: about:telemetry > data:application page
Path to .json: modules/data/about_telemetry.components.json
```
```
Selector Name: events-tab
Selector Data: "div[class='category category-no-icon has-data has-subsection'][value='events-section']"
Description: Events option
Location: about:telemetry Sidebar option
Path to .json: modules/data/about_telemetry.components.json
```
#### address_fill
```
Selector Name: form-field
Selector Data: "input[autocomplete='{name}']"
Description: Input field 
Location: Input field in the autofill address demo page - https://mozilla.github.io/form-fill-examples/basic.html
Path to .json: modules/data/address_fill.components.json
```
```
Selector Name: submit-button
Selector Data: "input[type='{name}']"
Description: "Submit" button
Location: At the bottom of the autofill address demo page - https://mozilla.github.io/form-fill-examples/basic.html
Path to .json: modules/data/address_fill.components.json
```
#### amo_languages
```
Selector Name: language-addons-title
Selector Data: "Card-header-text"
Description: Search results header
Location: Language addon search results header inside addons.mozilla.org/en-US/firefox/language-tools/
Path to .json: modules/data/amo_languages.components.json
```
```
Selector Name: language-addons-row
Selector Data: "tr[class='{name}']"
Description: The title row where the language is mentioned
Location: The row displaying the language addon’s name and details in the search results section of addons.mozilla.org/en-US/firefox/language-tools/
Path to .json: modules/data/amo_languages.components.json
```
```
Selector Name: language-addons-row-link
Selector Data: "a"
Description: The link with the desired language
Location: The clickable link within the search result section on the addons.mozilla.org/en-US/firefox/language-tools/ page, which directs users to the addon’s detailed page
Path to .json: modules/data/amo_languages.components.json
```
```
Selector Name: language-addons-subpage-add-to-firefox
Selector Data: "div[class='AMInstallButton AMInstallButton--noDownloadLink']"
Description: "Add to Firefox" button 
Location: The large blue button on the detailed addon page after being redirected from the search results on addons.mozilla.org/en-US/firefox/language-tools/
Path to .json: modules/data/amo_languages.components.json
```
```
Selector Name: language-install-popup-add
Selector Data: "button[class='popup-notification-primary-button primary footer-button']"
Description: Installation language add-on popup
Location: Hangs from the Extensions button in toolbar once the "Add button" was clicked
Path to .json: modules/data/amo_languages.components.json
```
```
Selector Name: language-addons-subpage-header
Selector Data: "AddonTitle"
Description: Tittle of the page
Location: The page title that displays the specific language addon name on the detailed addon page after being redirected from the search results on addons.mozilla.org/en-US/firefox/language-tools/
Path to .json: modules/data/amo_languages.components.json
```
#### amo_themes
```
Selector Name: recommended-addon
Selector Data: ".RecommendedAddons .SearchResult-result"
Description: Theme section results
Location: Recommended themes section inside addons.mozilla.org/en-US/firefox/themes/
Path to .json: modules/data/amo_themes.components.json
```
```
Selector Name: theme-title
Selector Data: "AddonTitle"
Description: Tittle of the page
Location: The page title that displays the specific theme addon name on the detailed addon page after being redirected from the recommended themes section on addons.mozilla.org/en-US/firefox/themes/
Path to .json: modules/data/amo_themes.components.json
```
```
Selector Name: install-button
Selector Data: "AMInstallButton-button"
Description: "Install Theme" button 
Location: The large blue button on the detailed addon page after being redirected from the recommended themes section on addons.mozilla.org/en-US/firefox/themes/
Path to .json: modules/data/amo_themes.components.json
```
#### autofill_popup
```
Selector Name: autofill-panel
Selector Data: "PopupAutoComplete"
Description: A dropdown panel displaying autofill suggestions for input fields (addresses, credit cards,login forms)
Location: Inside any autofill-eligible form field, triggered by user interaction such as a click or focus event
Path to .json: modules/data/autofill_popup.components.json
```
```
Selector Name: doorhanger-save-button
Selector Data: button[label='Save'].popup-notification-primary-button
Description: The "Save" button 
Location: Inside the autofill save doorhangers (address and credit card) that is triggered in navigation bar
Path to .json: modules/data/autofill_popup.components.json
```
```
Selector Name: doorhanger-dropdown-button
Selector Data: "button[aria-label='More actions']"
Description: The down arrow next to the "Not now" button 
Location: Inside the autofill save credit card doorhanger that is triggered in navigation bar
Path to .json: modules/data/autofill_popup.components.json
```
```
Selector Name: doorhanger-dropdown-never-save-cards-button
Selector Data: "menuitem[label='Never save cards']"
Description: The hidden button in save credit card doorhanger.
Location: Inside the autofill save credit card doorhanger, accessible by clicking the down arrow next to the "Not now" button
Path to .json: modules/data/autofill_popup.components.json
```
```
Selector Name: doorhanger-update-button
Selector Data: "button[label='Update']"
Description: The "Update" button 
Location: Inside the autofill save addreses doorhanger that is triggered in navigation bar
Path to .json: modules/data/autofill_popup.components.json
```
```
Selector Name: select-form-option
Selector Data: ".autocomplete-richlistbox .autocomplete-richlistitem"
Description: An individual entry within the autofill dropdown, representing a selectable suggestion such as a name, address, or card number
Location: Appears as part of the dropdown under the autofill panel, within any eligible form field when suggestions are available.
Path to .json: modules/data/autofill_popup.components.json
```
```
Selector Name: clear-form-option
Selector Data: ".autocomplete-richlistbox .autocomplete-richlistitem[ac-value='Clear Autofill Form']"
Description: The "Clear Autofill Form" option in the dropdown that appears when interacting with an autofill-enabled input field
Location: Appears as part of the dropdown under the autofill panel, within any eligible form field after a field was autofilled.
Path to .json: modules/data/autofill_popup.components.json
```
```
Selector Name: update-card-info-popup-button
Selector Data: "button[label='Update existing card']"
Description: The "Update existing card" button 
Location: Inside the autofill save credit card doorhanger that is triggered in navigation bar
Path to .json: modules/data/autofill_popup.components.json
```
```
Selector Name: cc-saved-options
Selector Data: "option[data-l10n-id='credit-card-label-number-name-expiration-2']"
Description: The actual "Add card" modal, containing 4 fields
Location: Inside the "Add card" form in the Saved payment methods section on the about:preferences#privacy page
Path to .json: modules/data/autofill_popup.components.json
```
```
Selector Name: cc-popup-button
Selector Data: "button[data-l10n-id='{name}']"
Description: "Add" button 
Location: Inside the "Saved payment methods" form in the Saved payment methods section on the about:preferences#privacy page
Path to .json: modules/data/autofill_popup.components.json
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
Location: Any text field cntext menu
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-suggest-strong-password
Selector Data: "fill-login-generated-password"
Description: Context menu option from Password field
Location: Login page - Password field context menu
Path to .json: modules/data/context_menu.components.json
```
```
Selector Name: context-menu-manage-passwords
Selector Data: selectorData": "manage-saved-logins
Description: Manage Passwords button
Location: Any login form field context menu
Path to .json: modules/data/context_menu.components.json
```
#### credit_card_fill
```
Selector Name: form-field
Selector Data: "input[autocomplete='{name}']"
Description: Input field
Location: Input field in the autofill credit card demo page - https://mozilla.github.io/form-fill-examples/basic_cc.html
Path to .json: modules/data/credit_card_fill.components.json
```
```
Selector Name: submit-button
Selector Data: "input[type='{name}']"
Description: "Submit" button
Location: "Submit" button at the bottom of the autofill credit card demo page - https://mozilla.github.io/form-fill-examples/basic_cc.html
Path to .json: modules/data/credit_card_fill.components.json
```
#### customize_firefox
```
Selector Name: forget
Selector Data: "wrapper-panic-button"
Description: The forget option button from the customizing options
Location: Customize firefox options in Context Chrome
Path to .json: modules/data/customize_firefox.components.json
```
```
Selector Name: history
Selector Data: "wrapper-history-panelmenu"
Description: The history button from the customizing options
Location: Customize firefox options in Context Chrome
Path to .json: modules/data/customize_firefox.components.json
```
```
Selector Name: library
Selector Data: "wrapper-library-button"
Description: The Library button from the customizing options
Location: Customize firefox options in Context Chrome
Path to .json: modules/data/customize_firefox.components.json
```
#### devtools
```
Selector Name: devtools-horizontal-splitter
Selector Data: "devtools-horizontal-splitter"
Description: The horizontal splitter that is used in the devtools
Location: On the devtools menu
Path to .json: modules/data/devtools.components.json
```
```
Selector Name: devtools-browser
Selector Data: "browser[aria-label='Developer Tools']"
Description: The devtools section of Firefox
Location: In the options of Firefox for opening the devtools
Path to .json: modules/data/devtools.components.json
```
#### error_page
```
Selector Name: error-title
Selector Data: ".title-text[data-l10n-id='dnsNotFound-title']"
Description: The error title name from the error page
Location: In the error page
Path to .json: modules/data/error_page.components.json
```
```
Selector Name: error-short-description
Selector Data: "errorShortDesc"
Description: The error short description from the error page
Location: In the error page
Path to .json: modules/data/error_page.components.json
```
```
Selector Name: error-suggestion-link
Selector Data: "#errorShortDesc a[data-l10n-name='website']"
Description: The link with the error suggestion
Location: In the error page
Path to .json: modules/data/error_page.components.json
```
```
Selector Name: error-long-description-items
Selector Data: "#errorLongDesc li"
Description: The error long description from the error page
Location: In the error page
Path to .json: modules/data/error_page.components.json
```
```
Selector Name: try-again-button
Selector Data: "#netErrorButtonContainer #neterrorTryAgainButton"
Description: The Try Again button from the error page
Location: In the error page
Path to .json: modules/data/error_page.components.json
```
#### example_page
```
Selector Name: title-header
Selector Data: "h1"
Description: "Example Domain" title
Location: The title of example.com page
Path to .json: modules/data/exemple_page.components.json
```
```
Selector Name: take-screenshot-box
Selector Data: "screenshotsPagePanel"
Description:  Page context menu option "Take Screenshot"
Location: Any non-linked content space inside example.com page
Path to .json: modules/data/exemple_page.components.json
```
```
Selector Name: more-information
Selector Data: "More information..."
Description: More information..." link
Location: The hyperlink positioned in the middle of example.com page
Path to .json: modules/data/exemple_page.components.json
```
#### find_toolbar
```
Selector Name: find-toolbar-input
Selector Data: "findbar-textbox"
Description: The find toolbar input area
Location: In the find toolbar
Path to .json: modules/data/find_toolbar.components.json
```
```
Selector Name: find-toolbar-close-button
Selector Data: "findbar-closebutton"
Description: The find toolbar close button
Location: In the find toolbar
Path to .json: modules/data/find_toolbar.components.json
```
```
Selector Name: next-match-button
Selector Data: "toolbarbutton[data-l10n-id='findbar-next']"
Description: The find toolbar next match button
Location: In the find toolbar
Path to .json: modules/data/find_toolbar.components.json
```
```
Selector Name: previous-match-button
Selector Data: "toolbarbutton[data-l10n-id='findbar-previous']"
Description: The find toolbar previous match button
Location: In the find toolbar
Path to .json: modules/data/find_toolbar.components.json
```
```
Selector Name: matches-label
Selector Data: "label.found-matches"
Description: The find toolbar all matches button
Location: In the find toolbar
Path to .json: modules/data/find_toolbar.components.json
```
```
Selector Name: find-status-label
Selector Data: "findbar-find-status"
Description: The find toolbar find status button
Location: In the find toolbar
Path to .json: modules/data/find_toolbar.components.json
```
```
Selector Name: reached-top-label
Selector Data: "description[data-l10n-id='findbar-wrapped-to-bottom']"
Description: The find toolbar status for reaching the top
Location: In the find toolbar
Path to .json: modules/data/find_toolbar.components.json
```
```
Selector Name: reached-bottom-label
Selector Data: "description[data-l10n-id='findbar-wrapped-to-top']"
Description: The find toolbar status for reaching the bottom
Location: In the find toolbar
Path to .json: modules/data/find_toolbar.components.json
```
#### forget_panel
```
Selector Name: forget-five-minutes
Selector Data: "PanelUI-panic-5min"
Description: The Forget Panel's option for 5 minutes
Location: In the Panel from the "Forget" toolbar button
Path to .json: modules/data/forget_panel.components.json
```
```
Selector Name: forget-two-hours
Selector Data: "PanelUI-panic-2hr"
Description: The Forget Panel's option for 2 hours
Location: In the Panel from the "Forget" toolbar button
Path to .json: modules/data/forget_panel.components.json
```
```
Selector Name: forget-one-day
Selector Data: "PanelUI-panic-day"
Description: The Forget Panel's option for 1 day
Location: In the Panel from the "Forget" toolbar button
Path to .json: modules/data/forget_panel.components.json
```
```
Selector Name: forget-confirm-button
Selector Data: "PanelUI-panic-view-button"
Description: The Forget Panel's Confirm button
Location: In the Panel from the "Forget" toolbar button
Path to .json: modules/data/forget_panel.components.json
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
Selector Name: input-field
Selector Data: input[autocomplete='{name}']
Description: Input field
Location: Input field in the autofill demo page
Path to .json: modules/data/login_autofill.components.json
```
```
Selector Name: username-field
Selector Data: input[placeholder='username']
Description: Username field
Location: Username field in the autofill demo page
Path to .json: modules/data/login_autofill.components.json
```
```
Selector Name: submit-form
Selector Data: input[value='Log In']
Description: Login button in the submit form
Location: Login button in the autofill demo page
Path to .json: modules/data/login_autofill.components.json
```
```
Selector Name: save-login-popup
Selector Data: notification-popup
Description: Save login doorhanger
Location: Save login doorhanger under the URL bar
Path to .json: modules/data/login_autofill.components.json
```
```
Selector Name: username-login-field
Selector Data: /html/body/div[1]/form[2]/input[1]
Description: Username login field
Location: Username field in the login demo page
Path to .json: modules/data/login_autofill.components.json
```
```
Selector Name: password-login-field
Selector Data: /html/body/div[1]/form[2]/input[2]
Description: Password login field
Location: Password field in the login demo page
Path to .json: modules/data/login_autofill.components.json
```
```
Selector Name: submit-button-login
Selector Data: /html/body/div[1]/form[2]/input[3]
Description: Login submit button
Location: Submit button in the login demo page 
Path to .json: modules/data/login_autofill.components.json
```
```
Selector Name: generated-securely-password
Selector Data: ".autocomplete-richlistbox .autocomplete-richlistitem[ac-value='Use a Securely Generated Password']"
Description: Use a Securely Generated Password option
Location: The dropdown under the password field in a login page
Path to .json: modules/data/login_autofill.components.json
```
#### navigation
```
Selector Name: awesome-bar
Selector Data: urlbar-input
Description: Awesome bar / URL bar
Location: Any clickable area on the awesome bar
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: results-dropdown
Selector Data: urlbar-results
Description: URL bar search results
Location: Any search result item from the URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: tab-to-search-text-span
Selector Data: urlbarView-dynamic-onboardTabToSearch-text-container
Description: Tab to search text span
Location: URL bar
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: search-mode-span
Selector Data: urlbar-search-mode-indicator-title
Description: Search mode span
Location: URL bar
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: overflow-item
Selector Data: [class='urlbarView-title urlbarView-overflowable']
Description: The title of every search result from the URL bar search results
Location: Any search result title item from the URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: search-one-off-settings-button
Selector Data: urlbar-anon-search-settings
Description: Search settings button
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: quick-actions-refresh-button
Selector Data: urlbarView-row-3-label-0
Description: Quick action refresh button
Location: URL bar
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: refresh-intervention-card
Selector Data: div[tip-type='intervention_refresh']
Description: 
Location:
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: fx-refresh-text
Selector Data: span[data-l10n-id='intervention-refresh-profile']
Description: Refresh Firefox button text
Location: URL bar results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: fx-refresh-button
Selector Data: span[role='button'][data-l10n-id='intervention-refresh-profile-confirm']
Description: Refresh Firefox button
Location: URL bar results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: fx-refresh-menu
Selector Data: span[data-l10n-id='urlbar-result-menu-button'][title='Open menu']
Description: Trending menu search results
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: fx-refresh-menu-get-help-item
Selector Data: menuitem[data-l10n-id='urlbar-result-menu-tip-get-help']
Description: Trending search results menu item
Location: Menu items for the trending results in the URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: fx-refresh-menu-get-help-item-get-help
Selector Data: urlbarView-result-menuitem
Description: Trending search results menu item
Location: Menu items for the trending results in the URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: search-engine-suggestion-row
Selector Data: div[class='urlbarView-row'][type='search_engine']
Description: Search suggestions from the URL bar search results
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: search-one-off-browser-button
Selector Data: urlbar-engine-one-off-item-{source}
Description: search one off buttons
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: panel-ui-button
Selector Data: PanelUI-button
Description: Panel UI button / hamburger menu
Location: Far right in the toolbar
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: navigation-background-component
Selector Data: nav-bar
Description: Navigation bar
Location: Any area on the navigation bar
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: context-menu-paste-and-go
Selector Data: paste-and-go
Description: Any search bar context menu option "paste-and-go" 
Location: Any search bar
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: private-browsing-icon
Selector Data: private-browsing-indicator-icon
Description: Private browsing icon
Location: Private browsing mode
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: add-extra-search-engine
Selector Data: [id*=urlbar-engine-one-off-item-engine--1][tooltiptext*='{0}']
Description: Add extra search engine in the url bar
Location: URL bar
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: search-one-off-engine-button
Selector Data: [id*=urlbar-engine-one-off-item-engine][tooltiptext^='{0}']
Description: Search one off engine button
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: downloads-button
Selector Data: downloads-button
Description: Toolbar download button
Location: Toolbar after downloading a file
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: search-results-container
Selector Data: urlbar-results
Description: URL bar search results
Location: Any search result item from the URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: addon-suggestion
Selector Data: div.urlbarView-row[type='rust_amo'] span.urlbarView-title.urlbarView-overflowable
Description: Addon suggestion in the URL bar search results
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: search-suggestion-list
Selector Data: div.urlbarView-row[type='search_engine'] span.urlbarView-title
Description: Search suggestion list
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: sponsored-suggestion
Selector Data: urlbarView-row-body-description
Description: Sponsored search results
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: firefox-suggest
Selector Data: div.urlbarView-row[label='Firefox Suggest'] > span.urlbarView-row-inner
Description: Firefox suggestion search results
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: search-result-autofill-adaptive-element
Selector Data: .//*[@type='autofill_adaptive']
Description: Search result autofill adaptive element
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: search-result
Selector Data: //div[@data-text-ad]//a
Description: ad search results
Location: URL bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: shield-icon
Selector Data: tracking-protection-icon-container
Description: Shield icon
Location: URL bar / Awseome bar after visiting a website
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: cryptominers
Selector Data: .protections-popup-category.subviewbutton.subviewbutton-iconic.subviewbutton-nav.blocked
Description: Cryptominer trackers
Location: Shield icon
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: no-trackers-detected
Selector Data: protections-popup-no-trackers-found-description
Description: No trackers detected
Location: Click on the shield icon
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: lock-icon
Selector Data: identity-icon
Description: Site information panel (Lock icon)
Location: URL bar / Awseome bar after visiting a website
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: connection-secure-button
Selector Data: identity-popup-security-button
Description: Connection secure button
Location: In the site information panel (lock icon)
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: more-information-button
Selector Data: identity-popup-more-info
Description: More information button in the connection security panel
Location: In the connection security insde the site information panel (lock icon)
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: search-result-url
Selector Data: .urlbarView-title.urlbarView-overflowable[is-url='']
Description: Search results url
Location: URL bar / Awesome bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: search-result-action-term
Selector Data: .urlbarView-action
Description: Search results entries
Location: URL bar / Awesome bar search results
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: refresh-button
Selector Data: reload-button
Description: Reload current page
Location: Toolbar
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: known-fingerprints
Selector Data: .protections-popup-category.subviewbutton.subviewbutton-iconic.blocked.subviewbutton-nav
Description: Known fingerprints
Location: Shield icon
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: fingerprints-blocked-subpanel
Selector Data: protections-popup-fingerprintersView
Description: Fingerprints subpanel
Location: Inside the shield incon in fingerprints subpanel
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: star-button
Selector Data: star-button-box
Description: Star button to bookmark a page
Location: URL bar
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: save-bookmark-button
Selector Data: editBookmarkPanelDoneButton
Description: Save bookmark
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: blue-star-button
Selector Data: image[id='star-button'][starred='true']
Description: Bookmarked page
Location: URL bar
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: download-panel-item
Selector Data: vbox[class='downloadContainer']
Description: Downloaded item in the download panel
Location: Download panel
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: edit-bookmark-panel
Selector Data: editBMPanel_namePicker
Description: Edit bookmark panel
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: remove-bookmark-button
Selector Data: editBookmarkPanelRemoveButton
Description: Remove bookmark button
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: forget-button
Selector Data: panic-button
Description: Forget button
Location: Toolbar after adding it from customize
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: history-button
Selector Data: history-panelmenu
Description: History button
Location: Toolbar after adding it from customize
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: library-button
Selector Data: library-button
Description: Library button
Location: Toolbar after adding it from customize
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: library-history-submenu-button
Selector Data: appMenu-library-history-button
Description: Library history submenu button
Location: Inside the library button in the toolbar
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: bookmarks-type-dropdown
Selector Data: editBMPanel_folderMenuList
Description: Bookmark location
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: bookmarks-type-dropdown-other
Selector Data: editBMPanel_unfiledRootItem
Description: Bookmark location - Other bookmarks
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: other-bookmarks
Selector Data: OtherBookmarks
Description: Other bookmarks option
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: other-bookmarks-popup
Selector Data: OtherBookmarksPopup
Description: Other bookmarks submenu
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: new-bookmark-name-field
Selector Data: editBMPanel_namePicker
Description: New bookmark name field
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: new-bookmark-url-field
Selector Data: editBMPanel_locationField
Description: New bookmark url field
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: new-bookmark-tags-field
Selector Data: editBMPanel_tagsField
Description: New bookmark tags field
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: new-bookmark-keyword-field
Selector Data: editBMPanel_keywordField
Description: New bookmark keyword field
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: bookmark-dialog
Selector Data: ookmarkpropertiesdialog
Description: Bookmark dialog
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: bookmark-accept-button
Selector Data: button[dlgtype='accept']
Description: Bookmark accept button
Location: Bookmark panel
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: bookmark-iframe
Selector Data: browser[class='dialogFrame']
Description: Add bookmark advanced
Location: Add bookmark from bookmarks sidebar
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: bookmark-robots
Selector Data: menuitem[label='Robots 2']
Description: A bookmark named robots
Location: A bookmark in other bookmarks
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: bookmark-current-tab
Selector Data: panelMenuBookmarkThisPage
Description: Bookmark current tab button
Location: Menu button / hamburger menu
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: password-notification-key
Selector Data: "box#notification-popup-box image#password-notification-icon.notification-anchor-icon"
Description: The key icon
Location: In the Navigation bar, next to the url input field
Path to .json: modules/data/navigation.components.json
```
```
Selector Name: password-update-doorhanger
Selector Data: "//*[contains(@class, 'popup-notification-description') and @popupid='password']"
Description: The password update doorhanger
Location: In the Navigation bar, next to the url input field, after the key icon was pressed
Path to .json: modules/data/navigation.components.json
```
#### panel_ui
```
Selector Name: panel-ui-button
Selector Data: PanelUI-menu-button
Description: Menu button / Hambuger menu
Location: Toolbar
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: sync-user-button
Selector Data: toolbarbutton[id='fxa-toolbar-menu-button']
Description: Account button
Location: Toolbar
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: fxa-manage-account-button
Selector Data: fxa-manage-account-button
Description: Sign in to sync button
Location: Account panel
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: sync-fxa
Selector Data: appMenu-fxa-status2
Description: Sync and save data
Location: Firefox menu
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: fxa-sign-in
Selector Data: #appMenu-fxa-status2 toolbarbutton
Description: Sign in button
Location: Firefox menu
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: fxa-sync-label
Selector Data: syncnow-label
Description: Sync now
Location: Firefox menu after singing in
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: new-private-window-option
Selector Data: appMenu-new-private-window-button2
Description: New private window buttin
Location: Firefox menu
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: more-tools
Selector Data: appMenu-more-button2
Description: More tools button
Location: Firefox menu
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: customize-toolbar
Selector Data: overflowMenu-customize-button
Description: Customize toolbar
Location: More tools inside Firefox menu
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: manage-themes
Selector Data: customization-lwtheme-link
Description: Manage themes
Location: On the hamburger menu > More Tools > Customize Toolbar > Manage Themes
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: zoom-reduce
Selector Data: appMenu-zoomReduce-button2
Description: Zoom reduce button
Location: Firefox menu
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: zoom-enlarge
Selector Data: appMenu-zoomEnlarge-button2
Description: Zoom enlarge button
Location: Firefox menu
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: zoom-reset
Selector Data: appMenu-zoomReset-button2
Description: Zoom reset button
Location: Firefox menu
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: find-in-page
Selector Data: appMenu-find-button2
Description: Find in page button
Location: Firefox menu
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: panel-ui-new-window
Selector Data: appMenu-new-window-button2
Description: New window button
Location: Firefox menu
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: panel-ui-history
Selector Data: appMenu-history-button
Description: History button
Location: Firefox menu
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: panel-ui-history-recently-closed
Selector Data: appMenuRecentlyClosedTabs
Description: Recently closed tabs
Location: On the hamburger menu > History
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: panel-ui-history-recently-closed-reopen-tabs
Selector Data: toolbarbutton[class='restoreallitem subviewbutton panel-subview-footer-button']
Description: Recently closed reopen tabs
Location: On the hamburger menu > History
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: panel-ui-new-private-window
Selector Data: appMenu-new-private-window-button2
Description: New private window
Location: Hamburger menu
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: recent-history-content
Selector Data: #appMenu_historyMenu .toolbarbutton-text
Description: Recent history content
Location: Hamburger menu
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: bookmark-item
Selector Data: toolbarbutton[class='subviewbutton subviewbutton-iconic bookmark-item']
Description: Bookmark item
Location: On the hamburger menu > Bookmarks
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: clear-recent-history
Selector Data: appMenuClearRecentHistory
Description: Clear recent history
Location: On the hamburger menu > History
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: panel-ui-history-recent-history-container
Selector Data: appMenu_historyMenu
Description: Recent history
Location: On the hamburger menu > History
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: panel-ui-history-recent-history-item
Selector Data: toolbarbutton
Description: Recent history item
Location: On the hamburger menu > History
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: panel-ui-bookmarks
Selector Data: appMenu-bookmarks-button
Description: Bookmark button
Location: On the hamburger menu
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: bookmark-by-title
Selector Data: toolbarbutton.bookmark-item[label*='{title}']
Description: Bookmark item
Location: On the hamburger menu > Bookmarks
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: bookmark-current-tab
Selector Data: panelMenuBookmarkThisPage
Description: Bookmark current tab button
Location: On the hamburger menu > Bookmarks
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: iframe
Selector Data: dialogFrame
Description: iframe
Location: iframe
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: clear-history-dropdown
Selector Data: sanitizeDurationPopup
Description: Clear browsing data and cookies by duration
Location: On the hamburger menu > History > Clear recent history
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: all-history-warning
Selector Data: sanitizeEverythingWarningBox
Description: Sanitize everything warning box
Location: On the hamburger menu > History > Clear recent history > Select everything from when
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: bookmark-location
Selector Data: editBMPanel_folderMenuList
Description: Bookmark location
Location: Bookmark panel
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: other-bookmarks
Selector Data: editBMPanel_unfiledRootItem
Description: Other bookmarks
Location: Bookmark panel
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: show-editor-when-saving-checkbox
Selector Data: editBookmarkPanel_showForNewBookmarks
Description: Show editor when saving checkbox
Location: Bookmark panel
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: other-bookmarks-toolbar
Selector Data: OtherBookmarks
Description: Other bookmarks toolbar
Location: Toolbar
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: other-bookmarks-by-title
Selector Data: menuitem.menuitem-iconic[label*='{title}']
Description: Bookmark item
Location: Toolbar
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: history-back-button
Selector Data: toolbarbutton.subviewbutton-back > image.toolbarbutton-icon
Description: History back button
Location: On the hamburger menu > History
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: history_title
Selector Data: //*[@id='PanelUI-history']//*[text()='History']
Description: History title
Location: On the hamburger menu > History
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: recently_closed_tabs
Selector Data: appMenuRecentlyClosedTabs
Description: Recently closed tabs button
Location: On the hamburger menu > History
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: recently_closed_windows
Selector Data: appMenuRecentlyClosedWindows
Description: Recently closed windows
Location: On the hamburger menu > History
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: search_history
Selector Data: appMenuSearchHistory
Description: Search history button
Location: On the hamburger menu > History
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: recent_history
Selector Data: panelMenu_recentHistory
Description: Recent history
Location: On the hamburger menu > History
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: manage_history
Selector Data: PanelUI-historyMore
Description: Manage history button
Location: On the hamburger menu > History
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: bookmark-tags
Selector Data: editBMPanel_tagsField
Description: Bookmark tage
Location: Bookmark panel
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: extend-bookmark-tags
Selector Data: editBMPanel_tagsSelectorExpander
Description: Extend bookmark tags
Location: Bookmark panel
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: work-tag
Selector Data: label[value='Work']
Description: Bookmark tag
Location: Bookmark panel
Path to .json: modules/data/panel_ui.components.json
```
```
Selector Name: todo-tag
Selector Data: label[value='To do']
Description: Bookmark tag
Location: Bookmark panel
Path to .json: modules/data/panel_ui.components.json
```
```
Selector name: password-button
Selector Data: "appMenu-passwords-button"
Description: Password button
Location: Hamburger Menu
```
#### text_area_form_autofill
```
Selector Name: street-address-textarea
Selector Data: "street-address"
Description: Input field 
Location: Input field in the autofill textarea select demo page
Path to .json: modules/data/text_area_form_autofill.components.json
```
```
