import os
from shutil import copyfile
from time import sleep

import pytest
from selenium.webdriver import ActionChains, Chrome, Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import PanelUi
from modules.page_object import AboutPrefs

TEST_PAGE_TITLE = "Home - Oregon State Parks"


@pytest.fixture()
def test_case():
    return "2084639"


@pytest.fixture()
def chrome_bookmarks(sys_platform, home_folder, tmp_path):
    source = os.path.join("data", "Chrome_Bookmarks")
    if sys_platform.lower().startswith("win"):
        target = os.path.join(
            home_folder,
            "AppData",
            "Local",
            "Google",
            "Chrome",
            "User Data",
            "Default",
            "Bookmarks",
        )
        app = os.path.join(
            home_folder, "AppData", "Local", "Google", "Chrome", "Application"
        )
    elif sys_platform == "Darwin":
        target = os.path.join(
            home_folder,
            "Library",
            "Application Support",
            "Google",
            "Chrome",
            "Default",
            "Bookmarks",
        )
        app = os.path.join("Applications", "Google Chrome.app")
    elif sys_platform == "Linux":
        target = os.path.join(
            home_folder, ".config", "google-chrome", "Default", "Bookmarks"
        )
        app = os.path.join("opt", "google", "chrome")
    try:
        fake_bookmarks = False
        fake_app = False
        if not os.path.exists(target):
            fake_bookmarks = True
            os.makedirs(os.path.dirname(target))
        else:
            os.rename(target, tmp_path / "Bookmarks")
        if not os.path.exists(app):
            fake_app = True
            os.makedirs(app)
        copyfile(source, target)
        yield target
        os.remove(target)
        if fake_bookmarks:
            os.removedirs(os.path.dirname(target))
        else:
            os.rename(tmp_path / "Bookmarks", target)
        if fake_app:
            os.removedirs(app)

    except FileNotFoundError:
        return None


def test_chrome_bookmarks_imported(chrome_bookmarks, driver: Firefox):
    if not chrome_bookmarks:
        pytest.skip("Google Chrome not installed or directory could not be created")
    about_prefs = AboutPrefs(driver, category="General")
    about_prefs.open()
    about_prefs.click_on("import-browser-data")
    about_prefs.import_bookmarks("Chrome")
    # Check bookmarks in PanelUI I guess?
    panel_ui = PanelUi(driver)
    panel_ui.item_exists_in_bookmarks(TEST_PAGE_TITLE)
