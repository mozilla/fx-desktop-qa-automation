import logging
import os
import subprocess
import sys
from shutil import copyfile
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Toolbar
from modules.page_object import AboutPrefs

TEST_PAGE_TITLE = (
    "The Humane Society of the United States| End suffering for all animals"
)


@pytest.fixture()
def add_prefs():
    return [
        ("browser.migrate.safari.get_permissions.enabled", True),
        ("devtools.chrome.enabled", True),
        ("devtools.debugger.remote-enabled", True),
    ]


@pytest.fixture()
def safari_prep():
    ascript = """
    tell application "Safari"
      activate
      open location "https://www.example.com"
      delay 5
      tell application "System Events"
        tell application process "Safari"
          set frontmost to true
          keystroke "d" using {command down}
          delay 2
          key code 36
          delay 2
        end tell
      end tell
      tell application "Safari" to if it is running then quit
    end tell
    """

    # Run the AppleScript using subprocess
    process = subprocess.run(
        ["osascript", "-e", ascript], text=True, capture_output=True
    )

    # Output the result
    if process.returncode == 0:
        logging.info("Bookmark added successfully.")
    else:
        logging.error(f"Error: {process.stderr}")
        assert False, "Failed to add safari bookmark"


@pytest.mark.skipif(sys.platform.lower() != "darwin", reason="Only testing on Mac")
def test_safari_bookmarks_imported(driver: Firefox, safari_prep):
    about_prefs = AboutPrefs(driver, category="General")
    about_prefs.open()
    about_prefs.click_on("import-browser-data")
    about_prefs.import_bookmarks("Safari", safari=True)
    toolbar = Toolbar(driver)
    toolbar.confirm_bookmark_exists(TEST_PAGE_TITLE)
