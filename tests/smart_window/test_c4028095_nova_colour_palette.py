"""
C4028095 / C4028096 - NOVA colour palette, dark and light
Verify the Smart Window chrome renders the NOVA palette in each colour scheme,
matching that scheme's reference image, and that the two schemes differ.
"""

import platform

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import SmartWindow
from modules.visual_baseline import VisualBaseline

pytestmark = pytest.mark.skipif(
    platform.system() != "Darwin",
    reason="Visual baselines have only been captured for macOS so far.",
)

# C4028095 is the dark palette, C4028096 the light one. The scheme has to be set
# before launch, so each runs as its own browser session.
SCHEMES = {"dark": 1, "light": 0}


@pytest.fixture()
def test_case():
    return ["4028095", "4028096"]


@pytest.fixture(params=sorted(SCHEMES))
def scheme(request):
    return request.param


@pytest.fixture()
def add_to_prefs_list(scheme):
    # Same signal Firefox's own ColorScheme mozscreenshots configuration uses.
    return [("ui.systemUsesDarkTheme", SCHEMES[scheme])]


def test_nova_colour_palette(
    driver: Firefox,
    smart_window: SmartWindow,
    visual_baseline: VisualBaseline,
    scheme: str,
):
    """
    C4028095 / C4028096 - NOVA colour palette, dark and light
    """
    smart_window.activate_smart_window()

    with driver.context(driver.CONTEXT_CHROME):
        toolbar = driver.find_element("id", "TabsToolbar")
        visual_baseline.expect_matches(toolbar, f"nova-palette-{scheme}")

        # The two schemes must not look the same, or a palette regression that
        # collapsed them into one would still match both references.
        other = "light" if scheme == "dark" else "dark"
        if visual_baseline.path_for(f"nova-palette-{other}").exists():
            visual_baseline.expect_differs(toolbar, f"nova-palette-{other}")
