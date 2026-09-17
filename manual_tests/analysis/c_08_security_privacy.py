"""Critical round -- security, privacy, permissions and enterprise policy.

Suites: 5833 (Security and Privacy), 6066 (DoH / enterprise policies),
1907 (WebRTC camera / microphone / screen sharing), 2130 (Firefox Accounts and Sync).

Enhanced Tracking Protection is very well covered: browser/components/preferences/tests/etp/
holds 14 tests for the preferences surface and
browser/base/content/test/protectionsUI/ holds 24 for the shield panel. WebRTC device sharing
likewise has a dedicated browser-chrome directory.

What stays manual splits into three groups: Windows parental controls and the DLP agent (both
need external software and an OS-level account), anything requiring live FxA credentials and
a second device, and the fingerprinting-protection font rows, which are content-rendering
comparisons.
"""

from _ledger import C
from c_util import CREST

ETP = "browser/components/preferences/tests/etp/"
PUI = "browser/base/content/test/protectionsUI/"
PRIV = "browser/components/preferences/tests/privacy/"
PERM = "browser/base/content/test/permissions/"
WEBRTC = "browser/base/content/test/webrtc/"

# ================================================================ tracking protection
C(
    5833,
    "STRONG",
    ETP + "browser_contentblocking.js; browser_contentblocking_categories.js; "
    "browser_etp_customize_1.js; browser_etp_customize_2.js; browser_etp_status.js; "
    + PUI
    + "browser_protectionsUI_state.js; browser_protectionsUI_shield_visibility.js",
    "The ETP category selector (Standard / Strict / Custom) and turning protection off are "
    "covered from the preferences side and from the shield panel's resulting state.",
    [103330, 446318],
)
C(
    5833,
    "STRONG",
    ETP + "browser_etp_exceptions_dialog.js; browser_cookie_exceptions_addRemove.js; "
    "browser_cookies_exceptions.js; "
    + PUI
    + "browser_protectionsUI_pbmode_exceptions.js",
    "browser_etp_exceptions_dialog.js and the cookie-exception tests add, persist and remove "
    "exceptions; browser_protectionsUI_pbmode_exceptions.js asserts private-window exceptions "
    "are not remembered, which is the negative case.",
    [107717, 107718],
)
C(
    5833,
    "STRONG",
    ETP
    + "browser_contentblocking_standard_tcp_section.js; browser_statePartitioning_strings.js; "
    "browser_statePartitioning_PBM_strings.js; "
    "browser/components/enterprisepolicies/tests/browser/browser_policy_cookie_settings.js",
    "The third-party cookie behaviour selector, its state-partitioning strings and the resulting "
    "cookieBehavior value.",
    [446333],
)
C(
    5833,
    "STRONG",
    "browser/components/preferences/tests/privacy/browser_sanitizeOnShutdown_prefLocked.js; "
    "browser/base/content/test/sanitize/browser_sanitizeOnShutdown_migration.js; "
    "browser/components/enterprisepolicies/tests/browser/browser_policy_sanitize_on_shutdown.js",
    "The clear-on-shutdown preference, what it selects, and the resulting sanitization are "
    "covered from the preferences pane, the migration path and the policy override.",
    [446334, 107103],
)
C(
    5833,
    "STRONG",
    PUI + "browser_protectionsUI.js; browser_protectionsUI_categories.js; "
    "browser_protectionsUI_trackers_subview.js; browser_protectionsUI_tracker_cookies_subview.js; "
    "browser_protectionsUI_cryptominers.js; browser_protectionsUI_socialtracking.js; "
    "browser_protectionsUI_fingerprinters.js",
    "Each blockable category has a test that loads tracking content and asserts it was blocked "
    "and reported in the shield panel.",
    [3956],
)
C(
    5833,
    "STRONG",
    PUI + "browser_protectionsUI_background_tabs.js; browser_protectionsUI_state.js; "
    "browser_protectionsUI_milestones.js; browser_protectionsUI_telemetry.js",
    "browser_protectionsUI_background_tabs.js is dedicated to when a background tab's blocked "
    "trackers are counted into the protections report -- the timing this case pins down.",
    [448309],
)
C(
    5833,
    "STRONG",
    PUI + "browser_protectionsUI_suspicious_fingerprinters_subview.js; "
    "browser_protectionsUI_fingerprinters.js; "
    + PERM
    + "browser_canvas_fingerprinting_resistance.js; browser_canvas_rfp_exclusion.js",
    "Suspected fingerprinters being blocked, and canvas randomisation following the ETP toggle "
    "including in third-party contexts, both have dedicated tests.",
    [2318651, 2230213],
)
C(
    5833,
    "STRONG",
    PRIV + "browser_privacy_gpc.js",
    "browser_privacy_gpc.js drives the Global Privacy Control / do-not-track preference and "
    "asserts which sessions the signal is sent in.",
    [446326],
)

# ================================================================ HTTPS-First
C(
    5833,
    "STRONG",
    "dom/security/test/https-first/browser_httpsfirst.js; browser_httpsfirst_console_logging.js; "
    "toolkit/components/httpsonlyerror/tests/browser/browser_errorpage.js",
    "browser_httpsfirst.js asserts the upgrade is attempted in normal browsing and falls back to "
    "HTTP when the server does not support it; browser_httpsfirst_console_logging.js asserts the "
    "console messages these two cases read.",
    [1362264, 1364748, 1364750],
)

# ================================================================ permissions
C(
    5833,
    "STRONG",
    PERM + "browser_permissions.js; browser_site_scoped_permissions.js; "
    "browser_temporary_permissions.js; browser_temporary_permissions_cross_origin_navigation.js; "
    "browser_permissions_postPrompt.js",
    "The permission panel, per-site scoping and the cross-origin iframe case are covered; "
    "browser_permissions.js also asserts which permissions are permanently denied and cannot be "
    "granted from a prompt.",
    [602563, 602565],
)
C(
    5833,
    "STRONG",
    PERM + "browser_temporary_permissions.js; browser_temporary_permissions_expiry.js; "
    "browser_temporary_permissions_navigation.js; browser_temporary_permissions_tabs.js",
    "The 'Remember this decision' persistence rules, including where the decision is *not* kept, "
    "are the subject of the temporary-permissions test group.",
    [602566],
)

# ================================================================ certificates and warnings
C(
    5833,
    "STRONG",
    "browser/base/content/test/siteIdentity/browser_identityPopup_HttpsOnlyMode.js; "
    "browser/base/content/test/siteIdentity/browser_secure_transport_insecure_scheme.js; "
    "browser/base/content/test/about/browser_aboutCertError_telemetry.js",
    "The identity popup's rendering of a site's certificate state is covered by the siteIdentity "
    "test group.",
    [3952],
)
C(
    5833,
    "STRONG",
    "browser/components/safebrowsing/content/test/browser_bug400731.js; browser_bug415846.js; "
    "browser_whitelisted.js; browser_mixedcontent_aboutblocked.js",
    "The Safe Browsing interstitial for unsafe sites, its report button and the allow-listing "
    "path are covered; browser_bug415846.js specifically covers when the report option is "
    "suppressed for non-Google-sourced blocks.",
    [3955, 50353],
)

# ================================================================ DoH / policies
C(
    6066,
    "STRONG",
    PRIV
    + "browser_privacy_dnsoverhttps.js; browser_privacy_dnsoverhttps_policy_srd.js; "
    "browser_privacy_dnsoverhttps_srd.js; toolkit/components/doh/test/browser/browser_trrSelect.js; "
    "browser_trrSelection_disable.js",
    "browser_privacy_dnsoverhttps_policy_srd.js is specifically about enterprise policy taking "
    "over the DoH setting, and browser_trrSelection_disable.js about DoH being disabled; the "
    "preferences tests cover setting the mode and provider.",
    [472133, 472134, 472135],
)
C(
    6066,
    "STRONG",
    "browser/base/content/test/captivePortal/browser_captivePortal_trr_mode3.js; "
    "browser/base/content/test/about/browser_aboutNetError_trr.js",
    "browser_captivePortal_trr_mode3.js drives a captive-portal session with TRR active, which "
    "is the network-transition condition this case describes.",
    [472136],
)
C(
    6066,
    "STRONG",
    "browser/base/content/test/captivePortal/browser_CaptivePortalWatcher.js; "
    "browser_CaptivePortalWatcher_1.js; browser_captivePortalTabReference.js; "
    "browser_closeCapPortalTabCanonicalURL.js; browser_captivePortal_certErrorUI.js",
    "The CaptivePortalWatcher tests drive a portal session through its whole lifecycle -- "
    "detection, the portal tab, re-checks and teardown -- which is what the 'prolonged session' "
    "claim rests on.",
    [943897],
)
C(
    6066,
    "STRONG",
    "browser/base/content/test/about/browser_aboutNetError.js; "
    "browser/base/content/test/about/browser_aboutCertError_telemetry.js; "
    "docshell/test/browser/browser_badCertDomainFixup.js",
    "SSL_ERROR_BAD_CERT_DOMAIN and its interstitial, including the www-suggestion fixup, are "
    "covered by the cert-error page tests.",
    [3404666],
)

# ================================================================ WebRTC device sharing
C(
    1907,
    "STRONG",
    WEBRTC
    + "browser_devices_get_user_media.js; browser_devices_get_user_media_screen.js; "
    "browser_devices_get_user_media_multi_process.js; "
    "browser_devices_get_user_media_default_permissions.js; browser_webrtc_hooks.js",
    "browser_devices_get_user_media.js walks the camera-only, microphone-only and combined "
    "audio+video permission panels and asserts both the allow and the deny outcome; "
    "browser_devices_get_user_media_screen.js covers choosing among multiple screens and windows "
    "in the share picker.",
    [122533, 122537, 122538, 122540, 122541, 122609],
)

# ================================================================ reviewed but kept
CREST(
    5833,
    "MEDIUM",
    PUI + "browser_protectionsUI.js; "
    "toolkit/components/contentanalysis/tests/browser/browser_print_content_analysis.js",
    "Three groups remain. Windows parental controls (child mode, Microsoft-account block/allow, "
    "time limits across Win8.1/10/11) need a real family account and OS configuration. The DLP "
    "agent rows need a third-party content-analysis agent installed -- the tree's "
    "contentanalysis tests use a mock agent, not the shipped one. The rest are visual: the "
    "Private Browsing theme and its High Contrast rendering, the clear-data icon after an "
    "update, and the fingerprinting-protection font rows, which compare rendered glyph metrics.",
)
CREST(
    6066,
    "MEDIUM",
    "n/a",
    "The Safe Search rows check that Google, YouTube, youtube-nocookie, m.youtube and "
    "youtube.googleapis receive the correct safe-search parameters -- live third-party endpoints. "
    "The remaining rows cover a DNS cache clear under DoH, http2 site loading and the "
    "system-proxy exceptions regression, none of which have a matching in-tree test.",
)
CREST(
    1907,
    "MEDIUM",
    "dom/serviceworkers/test/",
    "One row left: pinned pages backed by Service Workers opening correctly. Service worker "
    "lifetime is well tested in dom/serviceworkers, but not in combination with pinned tabs.",
)
CREST(
    2130,
    "MEDIUM",
    "services/sync/tests/; browser/base/content/test/sync/",
    "The whole suite needs live Firefox Accounts credentials and, for most rows, a second "
    "signed-in device: account creation, sign-in, password change and recovery, Send Tab to "
    "Device, desktop-to-desktop sync, and synced tabs appearing across devices. The tree tests "
    "the sync engines against a mocked server, which does not reach these flows.",
)
