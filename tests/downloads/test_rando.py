from selenium.webdriver import Firefox


def test_rando(driver: Firefox):
    driver.get("https://chatgpt.com/")
