import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage

APK_URL = "https://github.com/appium/android-apidemos/releases/download/v6.0.3/ApiDemos-debug.apk"
APK_NAME_REGEX = r".*\.apk(\s\(\d+\))?$"


@pytest.fixture()
def test_case():
    return "1836831"


@pytest.mark.headed
def test_download_apk_and_check_extension(driver: Firefox):
    """
    1836830: Verify the APK filename shown in Firefox Downloads panel includes `.apk`
    """
    nav = Navigation(driver)

    # Load a normal page
    page = GenericPage(driver, url="about:blank")
    page.open()

    # Simulate downloading the file by creating and clicking an anchor element
    driver.execute_script(
        """
        const url = arguments[0];
        const a = document.createElement("a");
        a.href = url;
        a.target = "_self";
        a.rel = "noopener noreferrer";
        document.body.appendChild(a);
        a.click();
        a.remove();
        """,
        APK_URL,
    )

    # Dismiss "harmful file" warning if present
    try:
        nav.click_file_download_warning_panel()
    except Exception:
        pass

    # Wait for the download entry in the panel
    nav.element_visible("download-target-element")

    # Reuse the verification that already worked
    nav.verify_download_name(APK_NAME_REGEX)
