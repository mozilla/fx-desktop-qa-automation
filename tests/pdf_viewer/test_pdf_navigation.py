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
    pdf_body = pdf_viewer.get_element("body")
    # page_one = pdf_viewer.get_element("pdf-page", labels=["1"])
    page_one_item = pdf_viewer.get_element("page-one-item")

    # initial_scroll_position = driver.execute_script("return { x: arguments[0].scrollLeft, y: arguments[0].scrollTop };", page_one_item)
    logging.info(page_one_item.location)

    # body.send_keys(Keys.DOWN)
    # Ensure the body element is focused
    sleep(10)

    # new_offset = driver.execute_script("return { x: arguments[0].scrollLeft, y: arguments[0].scrollTop };", page_one_item)

    logging.info(page_one_item.location)