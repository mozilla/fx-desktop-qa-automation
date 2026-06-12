from selenium.webdriver import Firefox, Keys

from modules.browser_object import ContextMenu, Glean, Navigation, PanelUi, TabBar
from modules.page_object import AboutNewtab, ExamplePage, GenericPage

SEARCH_TERM = "firefox"
# Commercial query so engines render the related-searches component that open_in_new_tab clicks.
# Spaces get URL-encoded, so match only the first token when checking the SERP URL.
RELATED_SEARCH_TERM = "women shoes"
RELATED_SEARCH_TERM_IN_URL = RELATED_SEARCH_TERM.split()[0]
PERSISTED_REFINEMENT = " browser"
IMAGE_PAGE_URL = "https://www.python.org/"

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
    """Open a new tab and perform a search via the URL bar.

    When params['is_private'] is set, the search runs in a new private browsing
    window so Firefox tags the impression with is_private='true'.
    """
    # Instantiate objects
    page = GenericPage(driver, url="about:newtab")
    nav = Navigation(driver)

    if params.get("is_private"):
        # Run the search in a new private browsing window so Firefox tags the impression
        # is_private='true'. Open it from the hamburger menu (not the keyboard shortcut),
        # which is robust to whatever surface currently holds focus.
        panel = PanelUi(driver)
        tabs = TabBar(driver)
        window_count = len(driver.window_handles)
        panel.open_private_window()
        tabs.wait_for_num_tabs(window_count + 1)
        tabs.switch_to_new_tab()
    else:
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


@_entry("unknown")
def _entry_unknown(driver: Firefox, search_term: str, params: dict = None):
    """Submit a urlbar search with Alt+Shift+Enter so the SERP opens in a new tab. Firefox cannot
    attribute the originating surface for a SERP opened this way, so it records source='unknown'."""
    # Instantiate objects
    page = GenericPage(driver, url="about:newtab")
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Open a new tab and submit the search into a new tab via Alt+Shift+Enter
    page.open()
    nav.search_in_new_tab_via_keyboard(search_term)

    # Switch to the SERP tab so it loads in the foreground and the impression is recorded
    tabs.wait_for_num_tabs(2)
    tabs.switch_to_new_tab()
    page.url_contains(search_term)


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
    image_page = GenericPage(driver, url=IMAGE_PAGE_URL)
    context_menu = ContextMenu(driver)

    # Open the page, right-click the image, and trigger the Google Lens search
    image_page.open()
    image = image_page.get_element("python-logo")
    image_page.scroll_to_element(image)
    image_page.context_click(image)
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
    glean = Glean(driver)
    search_bar_name = f"{params['engine'].lower()}-incontent-search-bar"

    # Open a new tab and perform the initial search
    page.open()
    nav.search(search_term)
    page.url_contains(search_term)

    # Wait for the first SERP impression to be recorded so Firefox has wired up in-content search telemetry before we
    # refine; otherwise the refinement is attributed as source='unknown'
    glean.poll_glean_metric("serp.impression", {"source": "urlbar"})

    # Refine the search via the in-content search bar and verify both the original term
    # and the refinement remain in the URL (guards against the engine auto-selecting and
    # replacing the existing query on focus)
    page.element_visible(search_bar_name)
    search_bar = page.get_element(search_bar_name)
    search_bar.click()
    search_bar.send_keys(Keys.END + PERSISTED_REFINEMENT + Keys.ENTER)
    page.url_contains(search_term)
    page.url_contains(PERSISTED_REFINEMENT.strip())


# ---------------------------------------------------------------------------
# Action flows — things that happen after the SERP is open
# ---------------------------------------------------------------------------


@_action("reload")
def _action_reload(driver: Firefox, params: dict = None):
    """Reload the SERP so Firefox records a fresh impression with source='reload'."""
    # Instantiate objects
    page = GenericPage(driver)
    nav = Navigation(driver)
    glean = Glean(driver)

    # Wait for the first SERP impression to be recorded so Firefox has wired up the SERP
    # telemetry context before we reload; otherwise the reload is attributed as source='unknown'
    page.url_contains(SEARCH_TERM)
    glean.poll_glean_metric("serp.impression", {"source": "urlbar"})

    # Reload the page and wait for it to settle
    nav.refresh_page()
    page.url_contains(SEARCH_TERM)


@_action("open_in_new_tab")
def _action_open_in_new_tab(driver: Firefox, params: dict = None):
    """Ctrl/Cmd+click a related-search shortcut on the SERP so the refined SERP opens in a new
    background tab, then switch to it so its impression records with source='opened_in_new_tab'."""
    # Instantiate objects
    page = GenericPage(driver)
    glean = Glean(driver)
    tabs = TabBar(driver)
    shortcut = f"{params['engine'].lower()}-related-search-shortcut"

    # Wait for the first SERP impression to be recorded so Firefox has wired up the SERP telemetry
    # context before we open the refinement; otherwise the new tab is attributed as source='unknown'
    page.url_contains(RELATED_SEARCH_TERM_IN_URL)
    glean.poll_glean_metric("serp.impression", {"source": "urlbar"})

    # Ctrl/Cmd+click the related-search shortcut to open the refined SERP in a new background tab
    page.element_visible(shortcut)
    page.open_link_in_new_tab_via_modifier_click(shortcut)

    # Switch to the new tab and wait for it to land on a results page. The related search differs
    # from the seed term and engines encode the query unpredictably (case, punctuation), so we
    # confirm a search URL (q=) loaded rather than matching the refined term text; the final Glean
    # poll verifies the impression itself.
    tabs.wait_for_num_tabs(2)
    tabs.switch_to_new_tab()
    page.url_contains("q=")


@_action("tabhistory")
def _action_tabhistory(driver: Firefox, params: dict = None):
    """Leave the SERP for another page, then return to it via the back button so Firefox
    records a fresh impression with source='tabhistory'.

    Navigating to a stable page rather than clicking an engine-specific search result keeps the
    flow engine-agnostic: the tabhistory attribution comes from the back navigation, not from how
    we left the SERP.
    """
    # Instantiate objects
    page = GenericPage(driver)
    nav = Navigation(driver)
    glean = Glean(driver)

    # Wait for the first SERP impression to be recorded so Firefox has wired up the SERP
    # telemetry context before we leave; otherwise the back navigation is attributed as source='unknown'
    page.url_contains(SEARCH_TERM)
    glean.poll_glean_metric("serp.impression", {"source": "urlbar"})

    # Leave the SERP for another page (creating a forward history entry), then return to the
    # SERP via tab history
    ExamplePage(driver).open()
    nav.click_back_button()
    page.url_contains(SEARCH_TERM)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_entry(driver: Firefox, entry: str, search_term: str, params: dict = None):
    """Look up and execute the registered entry flow by name."""
    params = params or {}
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
