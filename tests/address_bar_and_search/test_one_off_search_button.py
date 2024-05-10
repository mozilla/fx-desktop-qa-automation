from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object_navigation import Navigation


def test_amazon_one_off_search_button(driver: Firefox):
    amazon_one_off = Navigation(driver).open()
    amazon_one_off.click_awesome_bar()
    amazon_one_off.click_amazon_one_off_button()
    amazon_one_off.search_via_amazon_one_off_button("sunglasses")
    # amazon_one_off.type_in_awesome_bar_via_amazon_one_off("sunglasses")
    amazon_one_off.expect_in_content(EC.url_contains("amazon"))
    amazon_one_off.clear_awesome_bar()
