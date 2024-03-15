from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def test_google_search_code(driver):
    print(" - TEST: Verify Firefox search code for Google SERP")

    # Enter Search term in URL bar
    with driver.context(driver.CONTEXT_CHROME):
        driver.find_element(By.ID, "urlbar-input").send_keys("soccer" + Keys.RETURN)

    # Check that the search url contains the appropriate search code
    with driver.context(driver.CONTEXT_CONTENT):
        fx_code = "client=firefox-b-d"
        WebDriverWait(driver, 10).until(EC.title_contains("Google Search"))
        search_url = driver.current_url
        print("The current url is: " + str(search_url))
        assert fx_code in search_url
