import os
from shutil import copyfile

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu
from modules.page_object import GenericPdf


@pytest.fixture()
def test_case():
    return "2228202"


@pytest.fixture()
def temp_pdf(tmp_path):
    loc = tmp_path / "boeing_brochure.pdf"
    copyfile("data/boeing_brochure.pdf", loc)
    return loc


@pytest.mark.headed
def test_add_image_pdf(driver: Firefox, sys_platform, temp_pdf):
    """
    C2228202: Verify that the user is able to add an image to a PDF file.
    """
    pdf_viewer = GenericPdf(driver, pdf_url=f"file://{temp_pdf}").open()
    context_menu = ContextMenu(driver)
    pdf_viewer.add_image(os.path.abspath("data/goomy.png"), sys_platform)

    pdf_viewer.element_exists("added-goomy-image")
    pdf_viewer.element_visible("added-goomy-image")

    pdf_viewer.context_click("added-goomy-image")
    context_menu.click_and_hide_menu("pdfjs-delete")
