import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object_generics import GenericPage

SEARCH_TERM = "firefox"

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
    # Instantiate objects
    page = GenericPage(driver, url="about:newtab")
    nav = Navigation(driver)

    # Open the page and perform the search via the URL bar
    page.open()
    nav.search(search_term)


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
