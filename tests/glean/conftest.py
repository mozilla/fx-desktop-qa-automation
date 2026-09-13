"""
Glean suite fixtures.

A `pytest.skip` here reports as TestRail Blocked, not Untested (see `GLEAN_SUITE_ID` in
`organize_entries`). Only skip for a confirmed external condition a rerun could clear.
"""

import pytest

# The CI console window can fully occlude Fx, which throttles visibility-driven work and drops
# the ad-visibility metrics. Windows-only pref, inert elsewhere.
OCCLUSION_PREFS = [("widget.windows.window_occlusion_tracking.enabled", False)]


@pytest.fixture()
def suite_id():
    return ("S70197", "Glean Telemetry")


@pytest.fixture()
def prefs_list(add_to_prefs_list):
    prefs = list(OCCLUSION_PREFS)
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []
