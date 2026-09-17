"""Population + tier scheme for the Critical / not-yet-automated round (round 4).

Selection: priority_id == 4 (Critical) AND custom_automation_status != 4 (anything other
than "Automation Completed").

Same question as rounds 1-3 -- "is this already covered by a test in
mozilla-firefox/firefox?" -- but restricted to the Critical, not-yet-automated cases, and
with every case in the population given an explicit verdict rather than only the positives:

  STRONG  an in-tree test drives the same user flow and asserts the same user-visible
          outcome  ->  goes in CRITICAL_NOT_AUTOMATED_STRONG.csv
  MEDIUM  reviewed, but kept: the tree either does not reach the feature at all, or touches
          it at narrower scope or lower altitude (pref-only, telemetry-only, one variant of
          a matrix, component unit test where the case is end-to-end)

Cases are identified by their TestRail number, which is "C" followed by the export's `id`
field -- e.g. id 3163606 is C3163606.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import _ledger  # noqa: E402

TIERS = ("STRONG", "MEDIUM")


def by_id():
    out = {}
    for c in _ledger.cases():
        out.setdefault(c["id"], c)  # a handful of ids are duplicated rows in the export
    return out


def population():
    """{case_id: case} for every Critical, not-Automation-Completed case."""
    return {
        cid: c
        for cid, c in by_id().items()
        if c.get("priority_id") == 4 and c.get("custom_automation_status") != 4
    }


# TestRail's custom_automation_status field.
AUTOMATION_STATUS = {
    1: "Untriaged",
    2: "In progress",
    3: "Suitable for automation",
    4: "Completed",
    5: "Not suitable",
    None: "unset",
}

SUITE_NAMES = {
    65: "Find in page / PDF viewer",
    67: "Crash reporter",
    68: "Session Restore",
    73: "Printing",
    74: "Migration from other browsers",
    85: "Context menus",
    88: "Image formats",
    102: "Scrolling and zoom",
    498: "Geolocation",
    943: "Screenshots",
    1694: "Top sites / real-world web compat",
    1697: "Web compat / screen sharing overlay",
    1731: "Media playback",
    1907: "WebRTC camera / microphone / screen sharing",
    1940: "OS integration (taskbar, default browser, shell)",
    1977: "Graphics and hardware acceleration",
    1997: "Themes and appearance",
    1998: "Full screen",
    2052: "Uninstall and Refresh Firefox",
    2054: "Form Autofill",
    2085: "Find Toolbar",
    2103: "Tabbed Browser",
    2119: "Profiles",
    2126: "Reader View",
    2130: "Firefox Accounts and Sync",
    2241: "Preferences",
    2525: "Bookmarks Toolbar (+ History/Library)",
    2542: "DevTools eager evaluation (DevEd)",
    5202: "Default Browser Agent (Windows)",
    5252: "Installers (Windows / Mac / Linux)",
    5259: "Drag and drop / clipboard",
    5260: "Background Update Agent",
    5403: "New Tab page and preferences",
    5833: "Security and Privacy",
    6066: "DNS over HTTPS / enterprise policies",
    18105: "Accessibility (screen readers)",
    22801: "Language pack updates",
    23035: "Easy Setup onboarding",
    24370: "Third-party software interop",
    29219: "Downloads",
    42945: "about:firefoxview",
    43517: "Password manager",
    49853: "Third-party add-ons interop",
    53810: "Sidebar",
    54271: "Translate selection panel",
    65334: "Address Bar 138+",
    66659: "Copy Link to Highlight (text fragments)",
    67503: "New Tab Lists widget",
    69048: "Graphics rendering (WebRender)",
    69070: "Local Network / Device Access",
    69142: "Backup and Restore",
    69749: "about:settings#home",
    70279: "AI window / Smart Window",
    70723: "Rename tabs (Tab Notes)",
    71226: "Release smoke / regression matrix",
    71394: "Translate quick action / about:translations",
    73783: "Reduced Protection (PBM/ETP)",
    73807: "Backup and Restore (2nd suite)",
    76427: "ToU onboarding on Linux distros",
    95385: "New Tab widgets (timer, checklist)",
    97961: "Backup and Restore (3rd suite)",
    100482: "Share Folder / Curated Link Sharing",
    100547: "Private Window appearance (NOVA)",
    100943: "Saved credentials autofill dropdown",
    103289: "Onboarding (Smart Window, 2nd suite)",
    103666: "about:keyboard shortcut customization",
}
