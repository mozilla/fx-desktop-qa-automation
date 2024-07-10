from time import sleep

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import Navigation
from modules.page_object import AboutConfig, AboutPrefs


def test_default_search_provider_change(driver: Firefox):
    """
    C1365245 - This test makes sure that the default search
    provider can be changed and settings are applied
    """

    # Create objects
    nav = Navigation(driver).open()
    about_config = AboutConfig(driver)
    search_term = "what is life?"

    # enable search bar via about:config
    pref = "browser.search.widget.inNavBar"
    about_config.toggle_true_false_config(pref)
    nav.clear_awesome_bar()
    nav.set_content_context()
    sleep(1)

    # type some word->select 'Change search settings' when the search drop-down panel is opened.

    nav.type_in_search_bar(search_term)
    nav.click_on_change_search_settings_button()

    # switch to the second tab
    driver.switch_to.window(driver.window_handles[1])
    sleep(1)

    # check that the current URL is about:preferences#search
    assert driver.current_url == "about:preferences#search"

    # open a site, open search settings again and check if it's opened in a different tab
    driver.get("https://9gag.com/")
    nav.type_in_search_bar(search_term)
    nav.click_on_change_search_settings_button()
    assert driver.current_url == "https://9gag.com/"

    driver.switch_to.window(driver.window_handles[2])
    assert driver.current_url == "about:preferences#search"

    # Set a different provider as a default search engine
    about_prefs = AboutPrefs(driver, category="search").open()
    about_prefs.search_engine_dropdown().select_option("DuckDuckGo")

    # Open the search bar and type in a keyword and check if it's with the right provider
    nav.type_in_search_bar(search_term)
    with driver.context(driver.CONTEXT_CHROME):
        search_engine_name_element = driver.find_element(
            By.CSS_SELECTOR, ".searchbar-engine-name"
        )

        assert search_engine_name_element.get_attribute("value") == "DuckDuckGo Search"
