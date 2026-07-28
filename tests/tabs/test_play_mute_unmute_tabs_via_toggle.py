from os import listdir
from shutil import copyfile

import pytest
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
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


def _visible_audio_links(driver):
    try:
        video_links = driver.find_elements(By.CSS_SELECTOR, ".audiolink")

        if len(video_links) < 2:
            return False

        return (
            video_links
            if all(video_link.is_displayed() for video_link in video_links[:2])
            else False
        )
    except StaleElementReferenceException:
        return False


def _wait_for_audio_tab_state(
    driver,
    tabs,
    required_attributes,
    absent_attributes=(),
):
    def _state_matches(_):
        try:
            with driver.context(driver.CONTEXT_CHROME):
                for tab_index in AUDIO_TAB_INDICES:
                    tab = tabs.get_element(
                        "tab-by-index",
                        labels=[str(tab_index)],
                    )

                    if any(
                        tab.get_attribute(attribute) is None
                        for attribute in required_attributes
                    ):
                        return False

                    if any(
                        tab.get_attribute(attribute) is not None
                        for attribute in absent_attributes
                    ):
                        return False

                return True
        except (
            NoSuchElementException,
            StaleElementReferenceException,
        ):
            return False

    WebDriverWait(driver, WAIT_TIMEOUT).until(_state_matches)


def _click_audio_toggle(tabs):
    tabs.hover("tab-by-index", labels=["2"])
    tabs.element_clickable(
        "any-media-button-by-tab-index",
        labels=["2"],
    )
    tabs.click_on(
        "any-media-button-by-tab-index",
        labels=["2"],
    )


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
    for link_index in range(2):
        video_links = wait.until(_visible_audio_links)
        playlist_page.context_click(video_links[link_index])
        context_menu.click_and_hide_menu(
            "context-menu-open-link-in-tab",
        )

    # Wait for both audio tabs to open and reach the autoplay-blocked state.
    tabs.wait_for_num_tabs(3)
    _wait_for_audio_tab_state(
        driver,
        tabs,
        required_attributes=("activemedia-blocked",),
    )

    # Select both audio tabs while staying on the first tab.
    for tab_index in AUDIO_TAB_INDICES:
        tabs.control_click(
            "tab-by-index",
            labels=[str(tab_index)],
        )

    _wait_for_audio_tab_state(
        driver,
        tabs,
        required_attributes=(
            "multiselected",
            "activemedia-blocked",
        ),
    )

    for _ in range(2):
        # Play or unmute both selected tabs.
        _click_audio_toggle(tabs)
        _wait_for_audio_tab_state(
            driver,
            tabs,
            required_attributes=("soundplaying",),
            absent_attributes=("muted",),
        )

        # Mute both selected tabs.
        _click_audio_toggle(tabs)
        _wait_for_audio_tab_state(
            driver,
            tabs,
            required_attributes=("muted",),
        )
