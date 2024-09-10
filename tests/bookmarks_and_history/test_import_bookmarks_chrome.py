import logging
import os
import stat
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
def add_prefs():
    return [("browser.migrate.chrome.get_permissions.enabled", True)]


@pytest.fixture()
def chrome_bookmarks(sys_platform, home_folder, tmp_path):
    """Move test Bookmarks file to correct location, fake Chrome instead of installing"""
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
            os.path.splitdrive(home_folder)[0],
            "\\Program Files",
            "Google",
            "Chrome",
            "Application",
            "chrome.exe",
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
        app = os.path.join(
            "/Applications", "Google Chrome.app", "Contents", "MacOS", "Google Chrome"
        )
    elif sys_platform == "Linux":
        target = os.path.join(
            home_folder, ".config", "google-chrome", "Default", "Bookmarks"
        )
        app = os.path.join("/opt", "google", "chrome", "google-chrome")

    try:
        fake_bookmarks = False
        fake_app = False
        if not os.path.exists(target):
            logging.info("Faking bookmarks...")
            os.makedirs(os.path.dirname(target), exist_ok=True)
            fake_bookmarks = True
        else:
            logging.info("Bookmarks folder exists...")
            os.rename(target, tmp_path / "Bookmarks")
        copyfile(source, target)

        if not os.path.exists(app):
            # Fake the Chrome app
            logging.info("Faking Chrome...")
            os.makedirs(os.path.dirname(app), exist_ok=True)
            fake_app = True
            with open(app, "w") as fh:
                fh.write("")
            logging.info("Fake Chrome built.")
            if "win" not in sys_platform.lower():
                # Linux and maybe Mac need the file to be executable
                os.chmod(app, stat.IRWXU)
                logging.info("Fake Chrome chmodded.")

        yield target

    except (FileNotFoundError, NotADirectoryError, PermissionError):
        yield None

    # Teardown: We don't actually want to destroy the Chrome setup of local users
    if os.path.exists(target):
        os.remove(target)
    if fake_bookmarks:
        os.removedirs(os.path.dirname(target))
    elif os.path.exists(tmp_path / "Bookmarks"):
        os.rename(tmp_path / "Bookmarks", target)
    if fake_app:
        os.removedirs(app)


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
