import pytest


@pytest.fixture()
def suite_id():
    return ("18215", "Address Bar and Search 89+")


@pytest.fixture(scope="session")
def httpserver_listen_address():
    """Set port for local http server"""
    return ("127.0.0.1", 5312)


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = [
        ("browser.aboutConfig.showWarning", False),
        ("privacy.donottrackheader.enabled", False),
        ("telemetry.fog.test.localhost_port", 5312),
        ("datareporting.healthreport.uploadEnabled", True),
        ("browser.newtabpage.enabled", True),
        ("browser.newtabpage.activity-stream.system.showSponsored", True),
        ("browser.newtabpage.activity-stream.showSponsoredTopSites", True),
        ("browser.topsites.useRemoteSetting", True),
        ("browser.topsites.contile.enabled", True),
        ("browser.search.region", "US"),
        ("browser.urlbar.scotchBonnet.enableOverride", True),
    ]
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []


@pytest.fixture()
def search_modes():
    return {
        "site": ["Google", "Amazon", "Bing", "DuckDuckGo", "eBay", "Wikipedia"],
        "browser": [
            ("*", "Bookmarks"),
            ("%", "Tabs"),
            ("^", "History"),
            (">", "Actions"),
        ],
    }
