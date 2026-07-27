import logging
import os
from shutil import copyfile

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import AboutPrefs

TEST_PAGE_TITLE = "Home - Oregon State Parks"


@pytest.fixture()
def test_case():
    return "2084639"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.migrate.chrome.get_permissions.enabled", True),
        ("devtools.chrome.enabled", True),
        ("devtools.debugger.remote-enabled", True),
    ]


@pytest.fixture()
def chrome_bookmarks(driver: Firefox, sys_platform, home_folder, tmp_path):
    """Move test Bookmarks file to correct location, fake Chrome instead of installing."""
    bookmarks_source = os.path.join("data", "Chrome_Bookmarks")
    local_state_source = os.path.join("data", "Chrome_Local_State")

    # Get locations for Google Chrome profile data.
    if sys_platform.lower().startswith("win"):
        user_data_root = os.path.join(home_folder, "AppData", "Local")
        chrome_root = os.path.join(user_data_root, "Google", "Chrome", "User Data")
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
    bookmarks_backup = tmp_path / "Bookmarks"

    bookmarks_backed_up = False
    local_state_created = False
    created_fake_files = []
    created_directories = []

    try:
        if not os.path.exists(bookmarks_target):
            logging.warning("Faking install...")

            current_directory = defaults_folder
            while not os.path.exists(current_directory):
                created_directories.append(current_directory)

                parent_directory = os.path.dirname(current_directory)
                if parent_directory == current_directory:
                    break

                current_directory = parent_directory

            os.makedirs(defaults_folder, exist_ok=True)
            logging.warning("Directory made!")

            for fakefile in ["History", "Cookies"]:
                fakefile_path = os.path.join(defaults_folder, fakefile)

                if not os.path.exists(fakefile_path):
                    created_fake_files.append(fakefile_path)

                    with open(fakefile_path, "w") as fh:
                        fh.write("")

            logging.warning("History and Cookies made!")

            if not os.path.exists(local_state_target):
                logging.warning("Faking local state...")
                local_state_created = True
                copyfile(local_state_source, local_state_target)
        else:
            logging.warning("Install folder exists...")
            os.rename(bookmarks_target, bookmarks_backup)
            bookmarks_backed_up = True

        copyfile(bookmarks_source, bookmarks_target)
        logging.warning("Bookmarks copied!")

        yield bookmarks_target

    except (
        FileNotFoundError,
        IsADirectoryError,
        NotADirectoryError,
        PermissionError,
    ) as error:
        logging.warning(error)
        pytest.skip("Google Chrome not installed or directory could not be created")

    finally:
        # Teardown: We don't want to destroy the Chrome setup of local users.
        if os.path.exists(bookmarks_target):
            os.remove(bookmarks_target)

        if bookmarks_backed_up and os.path.exists(bookmarks_backup):
            os.rename(bookmarks_backup, bookmarks_target)

        for fakefile_path in created_fake_files:
            if os.path.exists(fakefile_path):
                os.remove(fakefile_path)

        if local_state_created and os.path.exists(local_state_target):
            os.remove(local_state_target)

        for directory in created_directories:
            try:
                os.rmdir(directory)
            except OSError:
                # Keep directories that contain pre-existing user data
                pass


def test_chrome_bookmarks_imported(
    chrome_bookmarks,
    driver: Firefox,
    sys_platform,
):
    about_prefs = AboutPrefs(driver, category="General")
    about_prefs.open()
    about_prefs.import_bookmarks("Chrome", sys_platform)

    toolbar = Navigation(driver)
    toolbar.confirm_bookmark_exists(TEST_PAGE_TITLE)
