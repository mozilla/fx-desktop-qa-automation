import pytest

from selenium.webdriver import Firefox

from modules.page_object import GenericPage, AboutPrefs, AboutConfig
from modules.browser_object import PanelUi, Navigation


@pytest.fixture()
def test_case():
    return "545733"


@pytest.fixture()
def temp_selectors():
    return {
        "yahoo-logo": {
            "selectorData": "sfp-placeholder",
            "strategy": "id",
            "groups": []
        }, 
        "yahoo-login-button": {
            "selectorData": "hd_nav_item",
            "strategy": "class",
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


WEBSITE_1 = "https://search.yahoo.com/"
WEBSITE_2 = "https://start.duckduckgo.com/"


def test_zoom_text_only_from_settings(driver: Firefox, temp_selectors):
    """
    C545733.1: Verify that ticking the zoom text only box would only affect the scale of text.
    Verify setting the default zoom level applies the chosen zoom level to all websites.
    """
    # Initializing objects
    web_page = GenericPage(driver, url=WEBSITE_1).open()    
    web_page.elements |= temp_selectors
    nav = Navigation(driver)

    # Save the original positions of elements for comparison
    driver.switch_to.new_window("tab")
    nav.search(WEBSITE_2)
    web_page.wait.until(
        lambda _: web_page.title_contains("DuckDuckGo")
    )
    original_positions = save_original_positions(driver, web_page)

    # Set the pref to zoom text only
    driver.switch_to.new_window("tab")
    about_prefs = AboutPrefs(driver, category="General").open()
    about_prefs.click_on("zoom-text-only")

    # Set zoom level to 110%
    about_prefs.set_default_zoom_level(110)

    # Verify results
    zoom_text_only_functionality_test(driver, nav, web_page, original_positions)

    # Reset the zoom settings so the config is no longer zoom text only, and default zoom level is 100%
    about_prefs = AboutPrefs(driver, category="General").open()
    about_prefs.set_default_zoom_level(100)
    about_prefs.click_on("zoom-text-only")


def test_zoom_text_only_after_restart(driver: Firefox, temp_selectors):
    """
    C545733.2: Verify that the zoom text only option works after restart
    """
    # Set the pref to zoom text only (simulate after restart)
    about_config = AboutConfig(driver)
    about_config.toggle_true_false_config("browser.zoom.full")

    # Initializing objects
    web_page = GenericPage(driver, url=WEBSITE_1).open()    
    web_page.elements |= temp_selectors
    nav = Navigation(driver)

    # Save the original positions of elements for comparison    
    driver.switch_to.new_window("tab")
    nav.search(WEBSITE_2)
    web_page.wait.until(
        lambda _: web_page.title_contains("DuckDuckGo")
    )
    original_positions = save_original_positions(driver, web_page)

    # Set default zoom level
    driver.switch_to.new_window("tab")
    about_prefs = AboutPrefs(driver, category="General").open()
    about_prefs.set_default_zoom_level(110)

    # Verify results
    zoom_text_only_functionality_test(driver, nav, web_page, original_positions)

    # Reset the zoom settings so the config is no longer zoom text only, and default zoom level is 100%
    about_prefs = AboutPrefs(driver, category="General").open()
    about_prefs.set_default_zoom_level(100)
    about_prefs.click_on("zoom-text-only")


def save_original_positions(driver, web_page):
    """
    Saves the original positions of elements to be tested to verify the effects of zooming
    """
    driver.switch_to.window(driver.window_handles[0])
    original_website1_image_position = web_page.get_element("yahoo-logo").location["x"]
    original_website1_text_position = web_page.get_element("yahoo-login-button").location["x"]
    driver.switch_to.window(driver.window_handles[1])
    original_website2_image_position = web_page.get_element("duckduckgo-logo").location["x"]
    original_website2_text_position = web_page.get_element("duckduckgo-tagline").location["x"]
    return (original_website1_image_position, original_website1_text_position, 
            original_website2_image_position, original_website2_text_position)


def zoom_text_only_functionality_test(driver, nav, web_page, original_positions):
    """
    Verifies that zoom text only works
    """
    (original_website1_image_position, original_website1_text_position, 
            original_website2_image_position, original_website2_text_position) = original_positions
    
    # Verify only text is enlarged
    driver.switch_to.window(driver.window_handles[0])
    new_image_position = web_page.get_element("yahoo-logo").location["x"]
    new_text_position = web_page.get_element("yahoo-login-button").location["x"]
    assert new_image_position == original_website1_image_position
    assert new_text_position < original_website1_text_position
    
    # Zoom out to 90% using panel controls
    panel = PanelUi(driver)
    panel.open_panel_menu()
    panel.click_on("zoom-reduce")
    panel.click_on("zoom-reduce")

    # Verify that zoom level badge is correct
    with driver.context(driver.CONTEXT_CHROME):
        nav.element_attribute_contains("toolbar-zoom-level", "label", "90%")

    # Verify that only text is zoomed out
    assert web_page.get_element("yahoo-logo").location["x"] == original_website1_image_position
    assert web_page.get_element("yahoo-login-button").location["x"] > original_website1_text_position

    # Verify that zoom level is default level for a different website and only text is enlarged
    driver.switch_to.window(driver.window_handles[1])
    assert web_page.get_element("duckduckgo-logo").location["x"] == original_website2_image_position
    assert web_page.get_element("duckduckgo-tagline").location["x"] < original_website2_text_position
