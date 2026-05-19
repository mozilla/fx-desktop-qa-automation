import time

import pytest
from selenium.webdriver import Firefox, Keys
from selenium.webdriver.common.by import By

from modules.browser_object import ContextMenu, Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object import AboutNewtab
from modules.page_object_example_page import ExamplePage
from modules.page_object_generics import GenericPage

SEARCH_TERM = "firefox"
PERSISTED_REFINEMENT = " browser"
WIKI_IMAGE_URL = "https://en.wikipedia.org/wiki/Norman_Rockwell"

_INCONTENT_SEARCH_BAR: dict[str, str] = {
    "Google": "textarea[aria-label='Search']",
    "Bing": "input#sb_form_q",
    "DuckDuckGo": "input[name='q']",
    "Ecosia": "input[name='q']",
    "Qwant": "input[name='q']",
}

ENTRY_PREFS: dict[str, list[tuple]] = {
    "urlbar_handoff": [
        ("browser.newtabpage.activity-stream.testing.shouldInitializeFeeds", True),
        ("browser.startup.page", 1),
    ],
    "urlbar_persisted": [
        ("browser.urlbar.showSearchTerms.enabled", True),
    ],
    "follow_on_from_refine_on_incontent_search": [
        ("browser.urlbar.showSearchTerms.enabled", True),
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
    image = wiki_page.get_element("wiki-article-image")
    wiki_page.scroll_to_element(image)
    wiki_page.context_click(image)
    context_menu.click_and_hide_menu("context-menu-search-image-with-lens")


@_entry("urlbar_searchmode")
def _entry_urlbar_searchmode(driver: Firefox, search_term: str, params: dict = None):
    """Enter search mode via the searchmode switcher for a specific engine, then search."""
    # Instantiate objects
    page = GenericPage(driver, url="about:newtab")
    nav = Navigation(driver)

    # Open a new tab, select the engine via the searchmode switcher, and perform the search
    page.open()
    nav.set_search_mode(params["engine"])
    nav.type_in_awesome_bar(search_term + Keys.ENTER)


@_entry("urlbar_persisted")
def _entry_urlbar_persisted(driver: Firefox, search_term: str, params: dict = None):
    """Perform an initial urlbar search, then refine it from the SERP to trigger a persisted impression."""
    # Instantiate objects
    page = GenericPage(driver, url="about:newtab")
    nav = Navigation(driver)

    # Open a new tab and perform an initial search
    page.open()
    nav.search(search_term)

    # Refine the persisted search term
    page.url_contains(search_term)
    nav.wait.until(lambda _: nav.get_awesome_bar_text() == search_term)
    nav.append_to_awesome_bar_and_submit(PERSISTED_REFINEMENT)
    page.url_contains(PERSISTED_REFINEMENT.strip())


@_entry("follow_on_from_refine_on_incontent_search")
def _entry_follow_on_from_refine_on_incontent_search(
    driver: Firefox, search_term: str, params: dict = None
):
    """Perform an initial urlbar search, then refine via the in-content SERP search bar."""
    # Instantiate objects
    page = GenericPage(driver, url="about:newtab")
    nav = Navigation(driver)
    engine = (params or {}).get("engine", "Google")
    selector = _INCONTENT_SEARCH_BAR[engine]

    # Open a new tab and perform the initial search
    page.open()
    nav.search(search_term)
    page.url_contains(search_term)

    # Wait until Firefox has fully classified the first SERP. The urlbar swapping
    # to show the search term (gated by browser.urlbar.showSearchTerms.enabled)
    # is the same "SERP classified" signal urlbar_persisted relies on; without
    # it, the refinement below races ahead and Firefox can't see the previous
    # SERP context, so the second impression gets source='unknown'.
    nav.wait.until(lambda _: nav.get_awesome_bar_text() == search_term)

    # Refine via the in-content search bar on the SERP. Wait for the SERP to
    # finish loading and give Firefox's SearchSERPTelemetry actor time to attach
    # before submitting — without this delay the refinement races ahead of the
    # content instrumentation and the resulting impression gets source='unknown'
    # instead of follow_on_from_refine_on_incontent_search. Submit by pressing
    # Enter on the searchbox itself: clicking the form's submit button is
    # tracked as a generic 'non_ads_link' engagement and breaks source tagging.
    search_bar = page.wait.until(
        lambda d: el
        if (el := d.find_element(By.CSS_SELECTOR, selector)).is_displayed()
        else False
    )
    page.wait.until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    time.sleep(3)

    search_bar.click()
    search_bar.send_keys(Keys.END)
    search_bar.send_keys(PERSISTED_REFINEMENT)
    page.wait.until(
        lambda _: search_bar.get_attribute("value").endswith(PERSISTED_REFINEMENT)
    )
    search_bar.send_keys(Keys.ENTER)
    page.url_contains(PERSISTED_REFINEMENT.strip())


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
