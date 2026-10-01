import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.components.dropdown import Dropdown
from modules.page_object import AboutConfig, AboutPrefs, AboutPrivatebrowsing

FEATURE_GATE_PREF = "browser.search.separatePrivateDefault.featureGate"
FIRST_ENGINE = "DuckDuckGo"
SECOND_ENGINE = "Bing"


@pytest.fixture()
def about_prefs_category():
    return "search"


@pytest.fixture()
def test_case():
    return "4105788"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.settings-redesign.enabled", True),
        (FEATURE_GATE_PREF, True),
        ("browser.aboutConfig.showWarning", False),
        # Lets the private page search box show the engine name.
        ("browser.urlbar.suggest.searches", True),
    ]


def check_private_engine(
    nav: Navigation, private_page: AboutPrivatebrowsing, engine: str
):
    """Check the engine in the address bar, searchbar and page search box."""
    nav.verify_search_mode_is_visible(engine)
    nav.element_attribute_contains(
        "legacy-searchmode-switcher-button", "aria-label", engine
    )
    private_page.element_attribute_contains(
        "search-handoff-button", "data-l10n-args", engine
    )


def test_private_default_search_engine_dropdown(
    driver: Firefox, about_prefs: AboutPrefs, nav: Navigation
):
    """
    C4105788 - The default search engine for private windows drop-down works as expected.
    """
    about_config = AboutConfig(driver)
    private_page = AboutPrivatebrowsing(driver)

    # Setup: add the searchbar to the toolbar.
    nav.add_search_bar_to_toolbar()

    # Step 1: Open search settings and turn on the private engine option.
    about_prefs.open()
    about_prefs.click_on("separate-private-engine-checkbox-input")
    about_prefs.element_attribute_is(
        "separate-private-engine-checkbox", "checked", "true"
    )

    # Step 2: Pick a different private engine.
    private_dropdown = Dropdown(
        about_prefs, root=about_prefs.get_element("private-engine-dropdown-root")
    )
    private_dropdown.select_option(FIRST_ENGINE)
    prefs_window = driver.current_window_handle

    # Step 3: Open a private window and check the engine everywhere.
    nav.open_and_switch_to_private_window_via_keyboard()
    private_window = driver.current_window_handle
    private_page.open()
    check_private_engine(nav, private_page, FIRST_ENGINE)

    # Step 4: Change the private engine again and check the private window.
    driver.switch_to.window(prefs_window)
    private_dropdown.select_option(SECOND_ENGINE)
    driver.switch_to.window(private_window)
    check_private_engine(nav, private_page, SECOND_ENGINE)

    # Step 5: Turn the option off in about:config.
    driver.switch_to.window(prefs_window)
    driver.switch_to.new_window("tab")
    about_config.toggle_true_false_config(FEATURE_GATE_PREF)

    # Step 6: Reload search settings and check the option is gone.
    about_prefs.open()
    # Wait for the page to load before checking the option is gone.
    about_prefs.element_visible("search-engine-dropdown-root")
    about_prefs.element_not_visible("separate-private-engine-checkbox")
