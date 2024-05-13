import pytest
from selenium.webdriver import Firefox
from modules.browser_object import Navigation

#Mapped each site name to the expected text from the awesome bar
sites = {
    "Google": "Google",
    "Bing": "Bing",
    "DuckDuckGo": "DuckDuckGo",
    "Wikipedia": "Wikipedia (en)",
}


@pytest.mark.parametrize("site", sites)
def test_search_one_off_button(driver: Firefox, site: str):
    # Saved the expected site name from the sites map
    site_name = sites[site]
    nav = Navigation(driver).open()
    nav.set_awesome_bar()
    nav.click_in_awesome_bar()
    nav.click_on_one_off_button(site)
    #Saved the expected text from the selected element for assertion
    expected_name = nav.get_element("search-mode-span").get_attribute("innerText")
    #Compare the text expected with the text from the awesome bar
    assert site_name == expected_name
