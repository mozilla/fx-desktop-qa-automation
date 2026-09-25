"""
Shared constants for theme-related tests.

Used by:
    - tests/theme_and_toolbar/test_customize_themes_and_redirect.py
    - tests/theme_and_toolbar/test_dark_theme_private_window.py
    - tests/theme_and_toolbar/test_installed_theme_enabled.py
"""

# Mozilla Addons host and theme path
AMO_HOST: str = "addons.mozilla.org"
AMO_THEMES_PATH: str = "firefox/themes"

# Theme element IDs as they appear in about:addons
COMPACT_DARK: str = "firefox-compact-dark_mozilla_org-heading"
COMPACT_LIGHT: str = "firefox-compact-light_mozilla_org-heading"
ALPENGLOW: str = "firefox-alpenglow_mozilla_org-heading"

# Human-readable titles as they appear in the "enabled-theme-title" element
COMPACT_DARK_TITLE: str = "Dark"
COMPACT_LIGHT_TITLE: str = "Light"
ALPENGLOW_TITLE: str = "Alpenglow"

# Expected background colors per theme (multiple values per theme are allowed)
THEMES: dict[str, list[str]] = {
    COMPACT_DARK: [
        "rgb(23, 21, 25)",  # nova dark, the default from Fx157 on
        "rgb(43, 42, 51)",  # classic darker tone
        "rgb(143, 143, 148)",  # focused dark
        "rgb(120, 119, 126)",  # dark without focus
    ],
    COMPACT_LIGHT: [
        "rgb(249, 249, 251)",
    ],
}

# Alpenglow renders differently depending on light / dark mode
ALPENGLOW_MAP: dict[str, str] = {
    "light": "rgba(255, 255, 255, 0.76)",
    "dark": "rgba(40, 29, 78, 0.96)",
}

# Colors observed for the navigation bar in a private window when
# `browser.theme.dark-private-windows = true`. Read via the same
# `navigation-background-component` element that activate_theme uses,
# so navbar colors differ from the old main-window palette.
PRIVATE_WINDOW_DARK: list[str] = [
    "rgb(62, 49, 95)",  # Nightly private-browsing tint
    "rgba(0, 0, 0, 0.2)",  # Beta 157 private-browsing overlay
]
