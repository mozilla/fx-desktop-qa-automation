import time
import pytest

from selenium.webdriver import Firefox
from pynput.keyboard import Key, Controller

from modules.page_object import AboutPrefs, GenericPage
from modules.browser_object import PanelUi, Navigation


@pytest.fixture()
def test_case():
    return "545733"


@pytest.fixture()
def temp_selectors():
    return {
        "google-logo": {
            "selectorData": "img[alt='Google']",
            "strategy": "css",
            "groups": []
        }, 
        "google-search-button": {
            "selectorData": "/html/body/div[1]/div[3]/form/div[1]/div[1]/div[4]/center/input[1]",
            "strategy": "xpath",
            "groups": []
        },
        "duckduckgo-logo": {
            "selectorData": "minimal-homepage_logoHorizontal__Q_hjO",
            "strategy": "class",
            "groups": []
        }, 
        "duckduckgo-tagline" : {
            "selectorData": "minimal-homepage_taglineText__owJPH",
            "strategy": "class",
            "groups": []
        }
    }

WEBSITE_1 = "https://www.google.com/"
WEBSITE_2 = "https://start.duckduckgo.com/"


@pytest.mark.headed
def test_zoom_text_only_from_prefs(driver: Firefox, temp_selectors):
    """
    C545733: Verify that ticking the zoom text only box would only affect the scale of text.
    Verify setting the default zoom level applies the chosen zoom level to all websites.
    """
    # Initializing objects
    web_page = GenericPage(driver, url=WEBSITE_1).open()    
    web_page.elements |= temp_selectors
    panel = PanelUi(driver)
    nav = Navigation(driver)
    keyboard = Controller()

    # Save the original positions of elements to verify the effects of zooming
    original_website1_image_position = web_page.get_element("google-logo").location["x"]
    original_website1_text_position = web_page.get_element("google-search-button").location["x"]
    driver.switch_to.new_window("tab")
    nav.search(WEBSITE_2)
    time.sleep(3)
    original_website2_image_position = web_page.get_element("duckduckgo-logo").location["x"]
    original_website2_text_position = web_page.get_element("duckduckgo-tagline").location["x"]

    # Set the pref to zoom text only
    driver.switch_to.new_window("tab")
    about_prefs = AboutPrefs(driver, category="General").open()
    about_prefs.click_on("zoom-text-only")

    # Set zoom level to 110%
    about_prefs.click_on("zoom-level")
    keyboard.press(Key.down)
    keyboard.press(Key.enter)

    # Verify only text is enlarged
    driver.switch_to.window(driver.window_handles[0])
    new_image_position = web_page.get_element("google-logo").location["x"]
    new_text_position = web_page.get_element("google-search-button").location["x"]
    assert new_image_position == original_website1_image_position
    assert new_text_position < original_website1_text_position
    
    # Zoom out to 90% using panel controls
    panel.open_panel_menu()
    panel.click_on("zoom-reduce")
    panel.click_on("zoom-reduce")
    time.sleep(1)

    # Verify that only text is zoomed out
    assert web_page.get_element("google-logo").location["x"] == original_website1_image_position
    assert web_page.get_element("google-search-button").location["x"] > original_website1_text_position

    # Verify that zoom level badge is correct
    with driver.context(driver.CONTEXT_CHROME):
        assert nav.get_element("toolbar-zoom-level").get_attribute("label") == "90%"

    # Verify that zoom level is default level for a different website and only text is enlarged
    driver.switch_to.window(driver.window_handles[1])
    assert web_page.get_element("duckduckgo-logo").location["x"] == original_website2_image_position
    assert web_page.get_element("duckduckgo-tagline").location["x"] < original_website2_text_position
