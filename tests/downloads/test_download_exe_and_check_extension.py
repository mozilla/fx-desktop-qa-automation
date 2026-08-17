import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage

EXE_URL = "https://javadl.oracle.com/webapps/download/AutoDL?BundleId=252907_0d06828d282343ea81775b28020a7cd3"
EXE_NAME_REGEX = r".*\.exe(\s\(\d+\))?$"


@pytest.fixture()
def test_case():
    return "1836829"


@pytest.mark.headed
def test_download_exe_and_check_extension(driver: Firefox):
    """
    1836829: Verify the EXE filename shown in Firefox Downloads panel includes `.exe`
    """
    nav = Navigation(driver)

    # Load a normal page
    page = GenericPage(driver, url="about:blank")
    page.open()

    # Simulate downloading the file by creating and clicking an anchor element
    driver.execute_script(
        """
        const a = document.createElement("a");
        a.href = arguments[0];
        a.click();
    """,
        EXE_URL,
    )

    # Dismiss "harmful file" warning if present
    try:
        nav.click_file_download_warning_panel()
    except Exception:
        pass

    # Wait for the download entry in the panel
    nav.element_visible("download-target-element")

    # Reuse the verification that already worked
    nav.verify_download_name(EXE_NAME_REGEX)
