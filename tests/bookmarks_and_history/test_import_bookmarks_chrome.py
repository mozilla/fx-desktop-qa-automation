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
    return [
        ("browser.migrate.chrome.get_permissions.enabled", True),
        ("devtools.chrome.enabled", True),
        ("devtools.debugger.remote-enabled", True),
    ]


@pytest.fixture()
def chrome_bookmarks(driver: Firefox, sys_platform, home_folder, tmp_path):
    """Move test Bookmarks file to correct location, fake Chrome instead of installing"""
    bookmarks_source = os.path.join("data", "Chrome_Bookmarks")
    local_state_source = os.path.join("data", "Chrome_Local_State")
    if sys_platform.lower().startswith("win"):
        user_data_root = os.path.join(home_folder, "AppData", "Local")
        chrome_root = os.path.join(user_data_root, "Google", "Chrome")
    elif sys_platform == "Darwin":
        user_data_root = os.path.join(home_folder, "Library", "Application Support")
        chrome_root = os.path.join(user_data_root, "Google", "Chrome")
    else:
        user_data_root = os.path.join(home_folder, ".config")
        chrome_root = os.path.join(user_data_root, "google-chrome")

    if not os.path.exists(user_data_root):
        logging.error(
            f"User data not stored where we expect it, {user_data_root} does not exist"
        )

    defaults_folder = os.path.join(chrome_root, "Default")
    bookmarks_target = os.path.join(defaults_folder, "Bookmarks")
    local_state_target = os.path.join(chrome_root, "Local State")

    try:
        fake_install = False
        if not os.path.exists(bookmarks_target):
            logging.warning("Faking install...")
            os.makedirs(defaults_folder, exist_ok=True)
            logging.warning("Directory made!")
            for fakefile in ["History", "Cookies"]:
                with open(os.path.join(defaults_folder, fakefile), "w") as fh:
                    fh.write("")
            logging.warning("History and Cookies made!")
            logging.warning("Faking local state...")
            copyfile(local_state_source, local_state_target)

            fake_install = True
        else:
            logging.warning("Install folder exists...")
            os.rename(bookmarks_target, tmp_path / "Bookmarks")
        copyfile(bookmarks_source, bookmarks_target)
        logging.warning("Bookmarks copied!")

        yield bookmarks_target

    except (FileNotFoundError, NotADirectoryError, PermissionError) as e:
        logging.warning(e)
        yield None

    # Teardown: We don't actually want to destroy the Chrome setup of local users
    if os.path.exists(bookmarks_target):
        os.remove(bookmarks_target)
    if fake_install:
        for fakefile in ["History", "Cookies"]:
            fake_fullpath = os.path.join(defaults_folder, fakefile)
            if os.path.exists(fake_fullpath):
                os.remove(fake_fullpath)
        os.remove(local_state_target)
        os.removedirs(defaults_folder)
    elif os.path.exists(tmp_path / "Bookmarks"):
        os.rename(tmp_path / "Bookmarks", bookmarks_target)


def test_chrome_bookmarks_imported(chrome_bookmarks, driver: Firefox):
    if not chrome_bookmarks:
        pytest.skip("Google Chrome not installed or directory could not be created")
    about_prefs = AboutPrefs(driver, category="General")
    about_prefs.open()
    about_prefs.click_on("import-browser-data")
    about_prefs.import_bookmarks("Chrome")
    # Check bookmarks in PanelUI I guess?
    panel_ui = PanelUi(driver)
    sleep(3)
    panel_ui.item_exists_in_bookmarks(TEST_PAGE_TITLE)
