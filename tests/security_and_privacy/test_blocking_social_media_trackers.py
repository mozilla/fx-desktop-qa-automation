import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TrustPanel
from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "446406"


SOCIAL_MEDIA_TRACKERS_URL = (
    "https://senglehardt.com/test/trackingprotection/test_pages/"
    "social_tracking_protection.html"
)


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("network.cookie.cookieBehavior", 0),
        ("privacy.trackingprotection.pbmode.enabled", False),
        ("privacy.trackingprotection.cryptomining.enabled", False),
        ("privacy.trackingprotection.fingerprinting.enabled", False),
        ("privacy.fingerprintingProtection.pbmode", False),
    ]


@pytest.mark.skip(reason="Blocked by bug 1866005. Tracked in bug 1940516.")
def test_blocking_social_media_trackers(
    driver: Firefox,
    nav: Navigation,
    trust_panel: TrustPanel,
    about_prefs_privacy: AboutPrefs,
):
    """
    C446406: Ensure that ETP Custom mode with the option "Cross-site tracking cookies,
    and isolate other cross-site cookies" set in the Cookies section blocks social media trackers.
    """
    about_prefs_privacy.open()
    about_prefs_privacy.select_trackers_to_block("cookies-isolate-social-media-option")

    driver.get(SOCIAL_MEDIA_TRACKERS_URL)

    trust_panel.open_panel()
    trust_panel.wait_for_trackers()
    trust_panel.trackers_blocked(
        "social-media-tracker"
    )  # TODO: Test and update string after bugfix
