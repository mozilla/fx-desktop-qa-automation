import pytest


@pytest.fixture()
def suite_id():
    return ("5403", "Pocket New Tab")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = [
        ("browser.newtabpage.enabled", True),
        ("browser.newtabpage.storageVersion", True),
        (
            "browser.newtabpage.activity-stream.asrouter.providers.cfr",
            '{"id":"cfr","enabled":true,"type":"remote-settings","collection":"cfr","updateCycleInMs":3600000}',
        ),
        (
            "browser.newtabpage.activity-stream.asrouter.providers.message-groups",
            '{"id":"message-groups","enabled":true,"type":"remote-settings","collection":"message-groups","updateCycleInMs":3600000}',
        ),
        (
            "browser.newtabpage.activity-stream.asrouter.providers.messaging-experiments",
            '{"id":"messaging-experiments","enabled":true,"type":"remote-experiments","updateCycleInMs":3600000}',
        ),
        (
            "browser.newtabpage.activity-stream.discoverystream.config",
            '{"api_key_pref":"extensions.pocket.oAuthConsumerKey","collapsible":true,"enabled":true}',
        ),
        ("browser.newtabpage.activity-stream.feeds.sections", True),
        ("browser.newtabpage.activity-stream.feeds.snippets", True),
        ("browser.newtabpage.activity-stream.feeds.system.topstories", True),
        ("browser.newtabpage.activity-stream.showSponsoredTopSites", True),
        ("browser.ping-centre.log", True),
        (
            "services.sync.prefs.sync.browser.newtabpage.activity-stream.showSponsoredTopSites",
            True,
        ),
    ]
    prefs.extend(add_to_prefs_list)
    return prefs
