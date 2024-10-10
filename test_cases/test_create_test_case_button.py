import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from pages.home_page import HomePage  

@pytest.fixture
def setup_browser():
    driver = webdriver.Firefox()
    yield driver
    driver.quit()

def test_clicking_create_test_case_button_opens_form(setup_browser):
    driver = setup_browser

    
    home_page = HomePage(driver)
    home_page.open()  

    
    create_test_case_button = driver.find_element(By.ID, "create-test-case-button")  


    create_test_case_button.click()

    