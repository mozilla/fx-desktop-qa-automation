import pytest
from selenium.webdriver import Firefox, Keys

from modules.browser_object import ContextMenu, Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object import AboutNewtab
from modules.page_object_example_page import ExamplePage
from modules.page_object_generics import GenericPage

SEARCH_TERM = "firefox"
WIKI_IMAGE_URL = "https://en.wikipedia.org/wiki/Norman_Rockwell"

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
    # Instantiate objects
    page = GenericPage(driver, url="about:newtab")
    nav = Navigation(driver)

    # Open the page and perform the search
    page.open()
    nav.search(search_term)


@_entry("searchbar")
def _entry_searchbar(driver: Firefox, search_term, params: dict = None):
    """Add the search bar from the Customize page, then perform a search via it."""
    # Instantiate objects
    nav = Navigation(driver)

    # Add the search bar to the toolbar and perform the search
    nav.add_search_bar_to_toolbar()
    nav.search_bar_search(search_term)


@_entry("urlbar_handoff")
def _entry_urlbar_handoff(driver: Firefox, search_term: str, params: dict = None):
    """Simulate a urlbar_handoff search: the newtab in-content search box is a fake input that,
    when clicked, activates the urlbar in handoff mode. Firefox records this origin and tags the
    SERP as source='urlbar_handoff'. reset=False preserves that handoff state while typing."""
    # Instantiate objects
    newtab = AboutNewtab(driver)
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Open a new tab and trigger a search via the newtab handoff input
    tabs.open_and_switch_to_new_tab()
    newtab.click_on("incontent-search-input")
    nav.set_awesome_bar()
    nav.type_in_awesome_bar(search_term + Keys.ENTER, reset=False)


@_entry("contextmenu")
def _entry_contextmenu(driver: Firefox, search_term: str, params: dict = None):
    """Select text on a page and search via the right-click context menu."""
    # Instantiate objects
    example = ExamplePage(driver)
    context_menu = ContextMenu(driver)

    # Open example.com, select the header text, and trigger the context menu search
    example.search_selected_header_via_context_menu()
    context_menu.click_and_hide_menu("context-menu-search-selected-text")


@_entry("contextmenu_visual")
def _entry_contextmenu_visual(driver: Firefox, search_term: str, params: dict = None):
    """Right-click an image and search via Google Lens from the context menu."""
    # Instantiate objects
    wiki_page = GenericPage(driver, url=WIKI_IMAGE_URL)
    context_menu = ContextMenu(driver)

    # Open the page, right-click the image, and trigger the Google Lens search
    wiki_page.open()
    wiki_page.wait_for_page_to_load()
    image = wiki_page.get_element("wiki-article-image")
    wiki_page.scroll_to_element(image)
    wiki_page.context_click(image)
    context_menu.click_and_hide_menu("context-menu-search-image-with-lens")


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
