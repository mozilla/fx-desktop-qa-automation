import pytest


@pytest.fixture()
def suite_id():
    return ("TODO", "Glean SERP Telemetry")


@pytest.fixture(scope="session")
def httpserver_listen_address():
    """Set port for local http server to receive Glean test pings"""
    return ("127.0.0.1", 5312)


@pytest.fixture()
def prefs_list(add_to_prefs_list):
    prefs = [
        ("browser.aboutConfig.showWarning", False),
        ("datareporting.healthreport.uploadEnabled", True),
        ("telemetry.fog.test.localhost_port", 5312),
        ("browser.urlbar.scotchBonnet.enableOverride", True),
    ]
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []
