import os
import sys
from shutil import copyfile

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object import AboutPrefs

NEWS_ARTICLE_TITLE = "Level 1, 2 evacuations issued for fire burning in Chelan"


@pytest.fixture()
def test_case():
    return "2084641"


@pytest.fixture()
def edge_bookmarks(sys_platform, home_folder):
    """
    C2084641: Verify that the user can Import Bookmarks from Microsoft Edge
    """
    source = os.path.join("data", "Edge_Bookmarks")
    if sys_platform.lower().startswith("win"):
        target = os.path.join(
            home_folder,
            "AppData",
            "Local",
            "Microsoft",
            "Edge",
            "User Data",
            "Default",
            "Bookmarks",
        )
    elif sys_platform == "Darwin":
        target = os.path.join(
            home_folder,
            "Library",
            "Application Support",
            "Microsoft Edge",
            "Default",
            "Bookmarks",
        )
    copyfile(source, target)
    return target


@pytest.mark.skipif(
    sys.platform.lower().startswith("linux"),
    reason="Only testing Edge on Win and MacOS",
)
@pytest.mark.skipif(
    os.environ.get("GITHUB_ACTIONS") == "true"
    and not sys.platform.lower().startswith("win"),
    reason="No GHA Mac",
)
def test_edge_bookmarks_imported(driver: Firefox, edge_bookmarks):
    about_prefs = AboutPrefs(driver, category="General")
    about_prefs.open()
    about_prefs.click_on("import-browser-data")
    about_prefs.import_bookmarks("Edge")
    nav = Navigation(driver)
    nav.confirm_bookmark_exists(NEWS_ARTICLE_TITLE)
