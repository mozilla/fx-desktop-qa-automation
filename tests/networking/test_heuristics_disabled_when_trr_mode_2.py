import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutConfig

TRR_MODE_PREF = "network.trr.mode"
TRR_MODE_DOH_ENABLED = 2
DISABLE_HEURISTICS_PREF = "doh-rollout.disable-heuristics"
HEURISTICS_DISABLED_VALUE = "true"


@pytest.fixture()
def test_case():
    return "922818"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.search.region", "US"),
        ("doh-rollout.home-region", "US"),
        ("doh-rollout.mode", 2),
        ("browser.aboutConfig.showWarning", False),
    ]


def test_heuristics_disabled_when_trr_mode_2(driver: Firefox):
    """
    C922818 - Verify that DoH heuristics are disabled when setting network.trr.mode to 2.
    """
    # Instantiate objects
    about_config = AboutConfig(driver)

    # Set network.trr.mode to 2 in about:config
    about_config.edit_config_value(TRR_MODE_PREF, TRR_MODE_DOH_ENABLED)

    # Firefox disables the DoH heuristics in response to the manual trr.mode change
    assert (
        about_config.get_pref_value(DISABLE_HEURISTICS_PREF)
        == HEURISTICS_DISABLED_VALUE
    )
