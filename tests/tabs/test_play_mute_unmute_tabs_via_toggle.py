from os import listdir
from shutil import copyfile

import pytest
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from modules.browser_object import ContextMenu, TabBar
from modules.page_object import GenericPage

AUDIO_TAB_INDICES = (2, 3)
WAIT_TIMEOUT = 30


@pytest.fixture()
def test_case():
    return "246981"


@pytest.fixture()
def local_doc_path(tmp_path, html_filename):
    for file in listdir("data/pages"):
        copyfile(f"data/pages/{file}", tmp_path / file)

    return (tmp_path / html_filename).resolve().as_uri()


@pytest.fixture()
def html_filename():
    return "web_audio_landing.html"


@pytest.fixture()
def add_to_prefs_list():
    return [("network.cookie.cookieBehavior", "2")]


def _wait_for_tab_attributes(
    driver: Firefox,
    tabs: TabBar,
    required_attributes: tuple[str, ...],
    description: str,
):
    last_state = {}

    def _attributes_match(_):
        nonlocal last_state

        try:
            current_state = {}

            with driver.context(driver.CONTEXT_CHROME):
                for tab_index in AUDIO_TAB_INDICES:
                    tab = tabs.get_tab(tab_index)

                    current_state[tab_index] = {
                        attribute: tab.get_attribute(attribute)
                        for attribute in (
                            "multiselected",
                            "activemedia-blocked",
                            "soundplaying",
                            "muted",
                        )
                    }

            last_state = current_state

            return all(
                all(
                    current_state[tab_index][attribute] is not None
                    for attribute in required_attributes
                )
                for tab_index in AUDIO_TAB_INDICES
            )

        except (
            NoSuchElementException,
            StaleElementReferenceException,
        ):
            return False

    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(_attributes_match)
    except TimeoutException as error:
        raise AssertionError(
            f"Timed out waiting for {description}. "
            f"Last observed tab state: {last_state}"
        ) from error


def _click_audio_toggle(tabs: TabBar):
    tabs.element_clickable(
        "any-media-button-by-tab-index",
        labels=["2"],
    )
    tabs.click_on(
        "any-media-button-by-tab-index",
        labels=["2"],
    )


# This test is unstable in Windows GHA for now
@pytest.mark.audio
def test_play_mute_unmute_tabs_via_toggle(
    driver: Firefox,
    local_doc_path,
):
    """
    C246981 - Verify that play/mute/unmute tabs via toggle audio works
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    playlist_page = GenericPage(driver, url=local_doc_path)
    playlist_page.open()

    # Locate and open the first 2 audio links in new tabs.
    video_links = wait.until(
        EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, ".audiolink")
        )
    )

    for link_index in range(2):
        playlist_page.context_click(video_links[link_index])
        context_menu.click_and_hide_menu(
            "context-menu-open-link-in-tab"
        )

    tabs.wait_for_num_tabs(3)

    # Replace the Windows-specific sleep with an explicit state wait.
    _wait_for_tab_attributes(
        driver,
        tabs,
        required_attributes=("activemedia-blocked",),
        description="both audio tabs to reach the autoplay-blocked state",
    )

    # Select both audio tabs while staying on the first tab.
    for tab_index in AUDIO_TAB_INDICES:
        tabs.control_click(tabs.get_tab(tab_index))

    _wait_for_tab_attributes(
        driver,
        tabs,
        required_attributes=("multiselected",),
        description="both audio tabs to become multiselected",
    )

    for iteration in range(2):
        # Play or unmute both selected tabs.
        _click_audio_toggle(tabs)

        _wait_for_tab_attributes(
            driver,
            tabs,
            required_attributes=("soundplaying",),
            description=(
                "both audio tabs to report sound playing "
                f"during iteration {iteration + 1}"
            ),
        )

        # Mute both selected tabs.
        _click_audio_toggle(tabs)

        _wait_for_tab_attributes(
            driver,
            tabs,
            required_attributes=("muted",),
            description=(
                "both audio tabs to become muted "
                f"during iteration {iteration + 1}"
            ),
        )
