import pytest
from selenium.webdriver import Firefox, Keys

from modules.browser_object import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object import AboutNewtab
from modules.page_object_generics import GenericPage

SEARCH_TERM = "firefox"

ENTRY_PREFS: dict[str, list[tuple]] = {
    "urlbar_handoff": [
        ("browser.newtabpage.activity-stream.testing.shouldInitializeFeeds", True),
        ("browser.startup.page", 1),
    ],
}

_ENTRIES = {}
_ACTIONS = {}


def _entry(name):
    """Decorator that registers a flow function as an entry surface by name.

    Entry flows navigate to a starting surface and trigger a search that opens the SERP.
    The name must match the 'entry' value used in cases.json.
    """

    def decorator(fn):
        _ENTRIES[name] = fn
        return fn

    return decorator


def _action(name):
    """Decorator that registers a flow function as a post-SERP action by name.

    Action flows run after the SERP is open and represent user interactions on the page.
    The name must match the 'action' value used in cases.json.
    """

    def decorator(fn):
        _ACTIONS[name] = fn
        return fn

    return decorator


# ---------------------------------------------------------------------------
# Entry flows — surfaces that open the SERP
# ---------------------------------------------------------------------------


@_entry("urlbar")
def _entry_urlbar(driver: Firefox, search_term, params: dict = None):
    """Open a new tab and perform a search via the URL bar."""
    page = GenericPage(driver, url="about:newtab")
    nav = Navigation(driver)

    page.open()
    nav.search(search_term)


@_entry("searchbar")
def _entry_searchbar(driver: Firefox, search_term, params: dict = None):
    """Add the search bar from the Customize page, then perform a search via it."""
    nav = Navigation(driver)

    nav.add_search_bar_to_toolbar()
    nav.search_bar_search(search_term)


@_entry("urlbar_handoff")
def _entry_urlbar_handoff(driver: Firefox, search_term: str, params: dict = None):
    """Click the newtab handoff search box, then type in the focused urlbar without refocusing."""
    newtab = AboutNewtab(driver)
    nav = Navigation(driver)
    tabs = TabBar(driver)

    tabs.open_and_switch_to_new_tab()
    newtab.click_on("incontent-search-input")
    nav.set_awesome_bar()
    nav.type_in_awesome_bar(search_term + Keys.ENTER, reset=False)


# ---------------------------------------------------------------------------
# Action flows — things that happen after the SERP is open
# ---------------------------------------------------------------------------

# TBD

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_entry(driver: Firefox, entry: str, search_term: str, params: dict = None):
    """Look up and execute the registered entry flow by name."""
    params = params or {}
    if entry == "unknown":
        pytest.skip("'unknown' source is not automatable")
    if entry not in _ENTRIES:
        raise NotImplementedError(f"Entry '{entry}' is not implemented")
    _ENTRIES[entry](driver, search_term, params)


def run_action(driver: Firefox, action: str, params: dict = None):
    """Look up and execute the registered action flow by name, or no-op if action is None."""
    if action is None:
        return
    params = params or {}
    if action not in _ACTIONS:
        raise NotImplementedError(f"Action '{action}' is not implemented")
    _ACTIONS[action](driver, params)
