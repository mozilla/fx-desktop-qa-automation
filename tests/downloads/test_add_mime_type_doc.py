import subprocess

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import AboutPrefs, GenericPage


@pytest.fixture()
def test_case():
    return "1756748"


DOC_LINK = "https://sapphire-hendrika-5.tiiny.site/"


@pytest.fixture()
def delete_files_regex_string():
    return r"sample.*\.doc"


def expected_app_name(sys_platform: str, opt_ci: bool) -> str:
    if sys_platform == "Darwin":
        return "TextEdit" if opt_ci else "Pages"
    return "LibreOffice Writer"


@pytest.mark.noxvfb
def test_mime_type_doc(driver: Firefox, sys_platform: str, opt_ci: bool, delete_files):
    """
    C1756748 - Verify that downloading a .doc file adds a new MIME type entry
    and the correct default application is assigned.
    """
    print(f"\n{'=' * 60}")
    print(f"Platform: {sys_platform}, CI: {opt_ci}")
    print(f"{'=' * 60}")

    if sys_platform == "Windows":
        print("\n--- Checking for LibreOffice ---")
        result = subprocess.run(
            ["where", "soffice.exe"], capture_output=True, text=True
        )
        print(f"LibreOffice installed: {result.returncode == 0}")
        if result.returncode == 0:
            print(f"Location: {result.stdout.strip()}")

    page = GenericPage(driver, url=DOC_LINK)
    nav = Navigation(driver)
    about_prefs = AboutPrefs(driver, category="general")

    print("\n--- Opening page and downloading ---")
    page.open()
    page.click_on("sample-doc-download")

    nav.set_always_open_similar_files()

    print("\n--- Opening about:preferences ---")
    about_prefs.open()

    print("\n--- Checking if MIME type exists ---")
    try:
        exists = about_prefs.element_exists(
            "mime-type-item", labels=["application/msword"]
        )
        print(f"MIME type exists: {exists}")
    except Exception as e:
        print(f"Error checking existence: {e}")
        exists = False

    if not exists:
        print("\n!!! MIME TYPE NOT FOUND !!!")
        driver.save_screenshot("artifacts/debug_no_mime.png")
        pytest.fail("MIME type entry was not created")

    print("\n--- Getting app name ---")
    app_name = about_prefs.get_app_name_for_mime_type("application/msword")
    expected = expected_app_name(sys_platform, opt_ci)

    print(f"\nResult: '{app_name}' vs Expected: '{expected}'")
    assert app_name == expected, f"Mismatch: got '{app_name}', expected '{expected}'"
    print("✓ TEST PASSED")

    if sys_platform == "Windows":
        print("\n--- Cleaning up ---")
        subprocess.run(
            ["taskkill", "/F", "/IM", "soffice.bin"], capture_output=True, check=False
        )
        subprocess.run(
            ["taskkill", "/F", "/IM", "soffice.exe"], capture_output=True, check=False
        )
