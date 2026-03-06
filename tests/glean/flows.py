import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object_generics import GenericPage

_ENTRIES = {}
_ACTIONS = {}


def _entry(name):
    def decorator(fn):
        _ENTRIES[name] = fn
        return fn
    return decorator


def _action(name):
    def decorator(fn):
        _ACTIONS[name] = fn
        return fn
    return decorator


# ---------------------------------------------------------------------------
# Entry flows — surfaces that open the SERP
# ---------------------------------------------------------------------------

@_entry("urlbar")
def _entry_urlbar(driver: Firefox, search_term: str, params: dict) -> None:
    GenericPage(driver, url="about:newtab").open()
    Navigation(driver).search(search_term)


@_entry("searchbar")
def _entry_searchbar(driver: Firefox, search_term: str, params: dict) -> None:
    raise NotImplementedError("searchbar entry not yet implemented")


@_entry("urlbar_handoff")
def _entry_urlbar_handoff(driver: Firefox, search_term: str, params: dict) -> None:
    raise NotImplementedError("urlbar_handoff entry not yet implemented")


@_entry("contextmenu")
def _entry_contextmenu(driver: Firefox, search_term: str, params: dict) -> None:
    raise NotImplementedError("contextmenu entry not yet implemented")


@_entry("contextmenu_visual")
def _entry_contextmenu_visual(driver: Firefox, search_term: str, params: dict) -> None:
    raise NotImplementedError("contextmenu_visual entry not yet implemented")


@_entry("urlbar_searchmode")
def _entry_urlbar_searchmode(driver: Firefox, search_term: str, params: dict) -> None:
    raise NotImplementedError("urlbar_searchmode entry not yet implemented")


@_entry("urlbar_persisted")
def _entry_urlbar_persisted(driver: Firefox, search_term: str, params: dict) -> None:
    raise NotImplementedError("urlbar_persisted entry not yet implemented")


@_entry("follow_on_from_refine_on_incontent_search")
def _entry_follow_on_incontent(driver: Firefox, search_term: str, params: dict) -> None:
    raise NotImplementedError("follow_on_from_refine_on_incontent_search entry not yet implemented")


@_entry("follow_on_from_refine_on_SERP")
def _entry_follow_on_serp(driver: Firefox, search_term: str, params: dict) -> None:
    raise NotImplementedError("follow_on_from_refine_on_SERP entry not yet implemented")


@_entry("system")
def _entry_system(driver: Firefox, search_term: str, params: dict) -> None:
    raise NotImplementedError("system entry not yet implemented")


@_entry("webextension")
def _entry_webextension(driver: Firefox, search_term: str, params: dict) -> None:
    raise NotImplementedError("webextension entry not yet implemented")


@_entry("about_newtab")
def _entry_about_newtab(driver: Firefox, search_term: str, params: dict) -> None:
    raise NotImplementedError("about_newtab entry not yet implemented")


@_entry("about_home")
def _entry_about_home(driver: Firefox, search_term: str, params: dict) -> None:
    raise NotImplementedError("about_home entry not yet implemented")


# ---------------------------------------------------------------------------
# Action flows — things that happen after the SERP is open
# ---------------------------------------------------------------------------

@_action("reload")
def _action_reload(driver: Firefox, params: dict) -> None:
    raise NotImplementedError("reload action not yet implemented")


@_action("tabhistory")
def _action_tabhistory(driver: Firefox, params: dict) -> None:
    raise NotImplementedError("tabhistory action not yet implemented")


@_action("open_in_new_tab")
def _action_open_in_new_tab(driver: Firefox, params: dict) -> None:
    raise NotImplementedError("open_in_new_tab action not yet implemented")


@_action("tab_close")
def _action_tab_close(driver: Firefox, params: dict) -> None:
    raise NotImplementedError("tab_close action not yet implemented")


@_action("navigation")
def _action_navigation(driver: Firefox, params: dict) -> None:
    raise NotImplementedError("navigation action not yet implemented")


@_action("back_navigation")
def _action_back_navigation(driver: Firefox, params: dict) -> None:
    raise NotImplementedError("back_navigation action not yet implemented")


@_action("refresh_navigation")
def _action_refresh_navigation(driver: Firefox, params: dict) -> None:
    raise NotImplementedError("refresh_navigation action not yet implemented")


@_action("window_close")
def _action_window_close(driver: Firefox, params: dict) -> None:
    raise NotImplementedError("window_close action not yet implemented")


@_action("click_non_ads")
def _action_click_non_ads(driver: Firefox, params: dict) -> None:
    raise NotImplementedError("click_non_ads action not yet implemented")


@_action("click_ads")
def _action_click_ads(driver: Firefox, params: dict) -> None:
    raise NotImplementedError("click_ads action not yet implemented")


@_action("click_ad_from_searchbar")
def _action_click_ad_from_searchbar(driver: Firefox, params: dict) -> None:
    raise NotImplementedError("click_ad_from_searchbar action not yet implemented")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_entry(driver: Firefox, entry: str, search_term: str, params: dict = None):
    params = params or {}
    if entry == "unknown":
        pytest.skip("'unknown' source is not automatable")
    if entry not in _ENTRIES:
        raise NotImplementedError(f"Entry '{entry}' is not implemented")
    _ENTRIES[entry](driver, search_term, params)


def run_action(driver: Firefox, action: str, params: dict = None):
    if action is None:
        return
    params = params or {}
    if action not in _ACTIONS:
        raise NotImplementedError(f"Action '{action}' is not implemented")
    _ACTIONS[action](driver, params)
