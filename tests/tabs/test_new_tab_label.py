import pytest


from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from modules.browser_object import ContextMenu, TabBar

@pytest.fixture()
def test_case():
    return "1339887"

def search_and_retrieve(driver:Firefox, alreadySearched):
    if not alreadySearched:
        searchBox = driver.find_element(By.ID, "search")
        searchBox.send_keys("context-openANewTab")
    else:
        #no need to search again, just refresh the page
        driver.switch_to.window(driver.window_handles[1]) #switches to "about:telemetry"
        driver.refresh()

    result = driver.find_element(By.XPATH, '//*[@id="context-openANewTab"]')
    # result.text returns "context-openANewTab (value)"
    value = result.text.split(" ")[-1]
    return value

def test_new_tab_label(driver:Firefox):
    tabs = TabBar(driver)
    tab_context_menu = ContextMenu(driver)

    url_list = ["about:logo", "about:telemetry"]
    driver.get(url_list[0])

    #get_tab index starts 1; NOT at 0!
    first_tab = tabs.get_tab(1) #about:logo

    #Step 1: Right click any opened tab and click New Tab
    tabs.context_click(first_tab)
    tab_context_menu.click_and_hide_menu("context-open-new-tab")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(url_list[1])
    result_1 = search_and_retrieve(driver, False)
    assert result_1 == "1", f"Expected 1 but got: {result_1}"

    second_tab = tabs.get_tab(2) #'about:telemetry' tab

    #Step 2: Right click a opened tab and hit W key on the keyboard
    tabs.context_click(second_tab)
    tabs.actions.send_keys("w").perform()
    result_2 = search_and_retrieve(driver, True)
    assert result_2 == "2", f"Expected 2 but got: {result_2}"

    #Step 3: Modified
    tabs.context_click(second_tab)
    tab_context_menu.click_and_hide_menu("context-open-new-tab")
    result_3 = search_and_retrieve(driver, True)
    assert result_3 == "3", f"Expected 3 but got: {result_3}"

 



