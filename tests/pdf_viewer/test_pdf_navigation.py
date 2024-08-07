import logging
from time import sleep

from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.page_object import GenericPdf

PDF_URL = "https://web.archive.org/web/20060818161558/http://archive.dovebid.com/brochure/bro1514.pdf"


def test_navigation_keys(driver: Firefox):
    """
    C3927.1: ensure that you can navigate through a PDF using keys
    """
    pdf_viewer = GenericPdf(driver, pdf_url=PDF_URL).open()
    body = pdf_viewer.get_element("html-body")

    # scroll down using arrow down key
    page_one_item = pdf_viewer.get_element("page-one-item")
    initial_location = page_one_item.location["y"]
    body.send_keys(Keys.DOWN)

    # wait for scrolling down
    pdf_viewer.wait.until(lambda _: page_one_item.location["y"] < initial_location)

    # scroll down using right key
    down_key_difference = abs(page_one_item.location["y"] - initial_location)
    initial_location = page_one_item.location["y"]
    body.send_keys(Keys.RIGHT)

    # wait for scrolling down, ensure that right key goes down more than down key
    pdf_viewer.wait.until(lambda _: page_one_item.location["y"] < initial_location)
    right_key_difference = abs(page_one_item.location["y"] - initial_location)
    assert right_key_difference > down_key_difference

    # scroll down using end key
    initial_location = page_one_item.location["y"]
    body.send_keys(Keys.END)

    # wait for scrolling down, ensure that end key goes down more than right key
    pdf_viewer.wait.until(lambda _: page_one_item.location["y"] < initial_location)
    end_key_difference = abs(page_one_item.location["y"] - initial_location)
    assert end_key_difference > right_key_difference

    # scroll up using up key
    initial_location = page_one_item.location["y"]
    body.send_keys(Keys.UP)

    # wait for scrolling up
    pdf_viewer.wait.until(lambda _: page_one_item.location["y"] > initial_location)

    # scroll up using left key
    up_key_difference = abs(page_one_item.location["y"] - initial_location)
    initial_location = page_one_item.location["y"]
    body.send_keys(Keys.LEFT)

    # wait for scrolling up, ensure that left key goes up more than up key
    pdf_viewer.wait.until(lambda _: page_one_item.location["y"] > initial_location)
    left_key_difference = abs(page_one_item.location["y"] - initial_location)
    assert left_key_difference > up_key_difference

    # scroll using home key
    initial_location = page_one_item.location["y"]
    body.send_keys(Keys.HOME)

    # wait for scrolling up, ensure that home key goes up more than left key
    pdf_viewer.wait.until(lambda _: page_one_item.location["y"] > initial_location)

    home_key_difference = abs(page_one_item.location["y"] - initial_location)
    assert home_key_difference > left_key_difference


def test_navigation_next_prev(driver: Firefox):
    """
    C3927.2: ensure that you can navigate through a PDF using next and previous keys
    """
    pdf_viewer = GenericPdf(driver, pdf_url=PDF_URL).open()

    page_one_item = pdf_viewer.get_element("page-one-item")
    initial_location = page_one_item.location["y"]
    pdf_viewer.get_element("scroll-next").click()

    pdf_viewer.wait.until(lambda _: page_one_item.location["y"] < initial_location)

    initial_location = page_one_item.location["y"]
    pdf_viewer.get_element("scroll-prev").click()

    pdf_viewer.wait.until(lambda _: page_one_item.location["y"] > initial_location)
