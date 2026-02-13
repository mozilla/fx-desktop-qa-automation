import pytest
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from modules.browser_object import PanelUi, TabBar
from modules.page_object_generics import GenericPage

TEST_URL = "https://ash-speed.hetzner.com/"


@pytest.fixture()
def test_case():
    return "1756696"


@pytest.fixture()
def extra_selectors():
    return {
        "downloads-private-got-it": {
            "selectorData": "[data-l10n-id='downloads-private-browsing-accept-button']",
            "strategy": "css",
            "groups": [],
        }
    }


@pytest.mark.headed
def test_close_browser_with_download_in_progress_shows_prompt(driver, extra_selectors):
    """
    C1756696 - Close Firefox while a download is in progress in Private Browsing
    and verify the 'Cancel All Downloads?' prompt is shown.
    """
    panel = PanelUi(driver)
    panel.elements |= extra_selectors
    page = GenericPage(driver, url=TEST_URL)
    tabs = TabBar(driver)

    # Step 1: Open a Private Browsing window
    panel.open_and_switch_to_new_window("private")

    # Step 2: Start a download (keep it in progress)
    page.open()
    page.click_on("sample-bin-download")

    # Step 3: Dismiss PB downloads interstitial if present
    try:
        panel.element_visible("downloads-private-got-it")
        panel.click_on("downloads-private-got-it")
        panel.element_not_visible("downloads-private-got-it")
    except TimeoutException:
        pass

    # Step 4: Close the Private Browsing window (closing last tab should close the window)
    tabs.close_first_tab_by_icon()

    # Step 5: Verify the native prompt text and accept it
    def alert_text_present(_):
        try:
            return panel.get_alert().text
        except NoAlertPresentException:
            return False

    alert_text = WebDriverWait(driver, 10).until(alert_text_present)
    text = alert_text.lower()

    assert "download will be canceled" in text
    assert "private browsing" in text
    assert ("leave private browsing" in text) or ("exit" in text)

    panel.get_alert().accept()

    # Step 6: Ensure we are attached to the remaining (non-private) window so teardown can quit
    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) >= 1)
    driver.switch_to.window(driver.window_handles[0])

    driver.quit()
