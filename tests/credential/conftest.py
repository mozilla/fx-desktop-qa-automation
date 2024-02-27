import pytest
from selenium.webdriver import Firefox

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


# TODO: Add test fixture fake creds
@pytest.fixture()
def populate_about_logins(driver: Firefox):
    def add_login(origin: str, username: str, password: str):
        origin_input = driver.find_element(By.CSS_SELECTOR, "input[name='origin']")
        origin_input.clear()
        origin_input.send_keys(origin, Keys.RETURN)
        username_input = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
        username_input.clear()
        username_input.send_keys(username, Keys.RETURN)
        password_input = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        password_input.clear()
        password_input.send_keys(password, Keys.RETURN)
        driver.find_element(By.CLASS_NAME, "save-changes-button").click()

    driver.get("about:logins")
