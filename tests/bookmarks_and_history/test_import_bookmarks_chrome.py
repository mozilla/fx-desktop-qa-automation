import errno
import logging
import os
from shutil import copyfileobj
from uuid import uuid4

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
def chrome_bookmarks(sys_platform, home_folder):
    """Prepare temporary Chrome profile data and restore existing data afterward."""
    bookmarks_source = os.path.join("data", "Chrome_Bookmarks")
    local_state_source = os.path.join("data", "Chrome_Local_State")

    if not os.path.isfile(bookmarks_source):
        pytest.fail(f"Test bookmarks file does not exist: {bookmarks_source}")

    # Get locations for Google Chrome profile data.
    if sys_platform.lower().startswith("win"):
        user_data_root = os.path.join(home_folder, "AppData", "Local")
        chrome_root = os.path.join(
            user_data_root,
            "Google",
            "Chrome",
            "User Data",
        )
    elif sys_platform == "Darwin":
        user_data_root = os.path.join(
            home_folder,
            "Library",
            "Application Support",
        )
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

    bookmarks_backup = None
    bookmarks_backed_up = False
    test_bookmarks_created = False
    local_state_created = False
    created_fake_files = []
    created_directories = []

    def _remove_created_file(path, description):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except OSError as error:
            logging.warning(f"Could not remove {description}: {error}")

    try:
        # Setup errors are handled here, separately from errors raised by the test.
        try:
            current_directory = defaults_folder

            while not os.path.exists(current_directory):
                created_directories.append(current_directory)
                parent_directory = os.path.dirname(current_directory)

                if parent_directory == current_directory:
                    break

                current_directory = parent_directory

            os.makedirs(defaults_folder, exist_ok=True)

            if os.path.exists(bookmarks_target):
                if not os.path.isfile(bookmarks_target):
                    raise IsADirectoryError(
                        f"Chrome Bookmarks path is not a file: {bookmarks_target}"
                    )

                logging.warning("Install folder exists...")

                bookmarks_backup = os.path.join(
                    defaults_folder,
                    f"Bookmarks.{uuid4().hex}.backup",
                )
                os.replace(bookmarks_target, bookmarks_backup)
                bookmarks_backed_up = True

            else:
                logging.warning("Faking install...")
                logging.warning("Directory made!")

                for fakefile in ["History", "Cookies"]:
                    fakefile_path = os.path.join(defaults_folder, fakefile)

                    if os.path.exists(fakefile_path):
                        continue

                    try:
                        with open(fakefile_path, "x"):
                            pass
                    except FileExistsError:
                        continue

                    created_fake_files.append(fakefile_path)

                logging.warning("History and Cookies made!")

                if os.path.exists(local_state_target):
                    if not os.path.isfile(local_state_target):
                        raise IsADirectoryError(
                            f"Chrome Local State path is not a file: "
                            f"{local_state_target}"
                        )
                else:
                    if not os.path.isfile(local_state_source):
                        pytest.fail(
                            f"Test local state file does not exist: "
                            f"{local_state_source}"
                        )

                    logging.warning("Faking local state...")

                    try:
                        with open(local_state_source, "rb") as source_file:
                            with open(local_state_target, "xb") as target_file:
                                local_state_created = True
                                copyfileobj(source_file, target_file)
                    except FileExistsError:
                        local_state_created = False

                        if not os.path.isfile(local_state_target):
                            raise IsADirectoryError(
                                f"Chrome Local State path is not a file: "
                                f"{local_state_target}"
                            )

            try:
                with open(bookmarks_source, "rb") as source_file:
                    with open(bookmarks_target, "xb") as target_file:
                        test_bookmarks_created = True
                        copyfileobj(source_file, target_file)
            except FileExistsError as error:
                raise FileExistsError(
                    f"Chrome Bookmarks file appeared during setup: {bookmarks_target}"
                ) from error

            logging.warning("Bookmarks copied!")

        except OSError as error:
            logging.warning(error)
            pytest.skip("Google Chrome not installed or directory could not be created")

        yield

    finally:
        # Restore existing bookmarks or remove the bookmarks created by the test.
        if bookmarks_backed_up and bookmarks_backup:
            try:
                os.replace(bookmarks_backup, bookmarks_target)
            except OSError as error:
                logging.warning(
                    "Could not restore original bookmarks. "
                    f"The backup remains at {bookmarks_backup}: {error}"
                )
        elif test_bookmarks_created:
            _remove_created_file(bookmarks_target, "test bookmarks")

        for fakefile_path in created_fake_files:
            _remove_created_file(fakefile_path, "fake Chrome file")

        if local_state_created:
            _remove_created_file(local_state_target, "fake local state")

        for directory in created_directories:
            try:
                os.rmdir(directory)
            except FileNotFoundError:
                pass
            except OSError as error:
                if error.errno not in (errno.ENOTEMPTY, errno.EEXIST):
                    logging.warning(
                        f"Could not remove created directory {directory}: {error}"
                    )


@pytest.mark.usefixtures("chrome_bookmarks")
def test_chrome_bookmarks_imported(driver: Firefox, sys_platform):
    about_prefs = AboutPrefs(driver, category="General")
    about_prefs.open()
    about_prefs.import_bookmarks("Chrome", sys_platform)

    toolbar = Navigation(driver)
    toolbar.confirm_bookmark_exists(TEST_PAGE_TITLE)
