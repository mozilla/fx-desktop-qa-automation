import os

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu
from modules.page_object import GenericPdf

PDF_URL = "https://web.archive.org/web/20060818161558/http://archive.dovebid.com/brochure/bro1514.pdf"


@pytest.mark.headed
def test_add_image_pdf(driver: Firefox, sys_platform, absolute_path: str):
    """
    C2228202: Verify that the user is able to add an image to a PDF file
    """
    pdf_viewer = GenericPdf(driver, pdf_url=PDF_URL).open()
    context_menu = ContextMenu(driver)
    pdf_viewer.add_image(os.path.join(absolute_path, "images/goomy.png"), sys_platform)

    pdf_viewer.element_exists("added-goomy-image")
    pdf_viewer.element_visible("added-goomy-image")

    pdf_viewer.context_click("added-goomy-image")
    context_menu.click_and_hide_menu("pdfjs-delete")
