import os
from pathlib import Path

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu
from modules.page_object import GenericPdf

# Constants
IMAGE_FILE_NAME = "goomy.png"
ADDED_IMAGE_ELEMENT = "added-goomy-image"
DELETE_MENU_OPTION = "pdfjs-delete"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def test_case():
    return "2228202"


@pytest.mark.headed
def test_add_image_pdf(driver: Firefox, sys_platform, pdf_viewer: GenericPdf):
    """
    C2228202: Verify that the user is able to add an image to a PDF file.

    Arguments:
        sys_platform: Current System Platform Type
        pdf_viewer: instance of GenericPdf with correct path.
    """
    context_menu = ContextMenu(driver)
    image_path = Path("data") / IMAGE_FILE_NAME
    pdf_viewer.add_image(str(image_path.absolute()), sys_platform)

    pdf_viewer.element_exists(ADDED_IMAGE_ELEMENT)
    pdf_viewer.element_visible(ADDED_IMAGE_ELEMENT)

    pdf_viewer.context_click(ADDED_IMAGE_ELEMENT)
    context_menu.click_and_hide_menu(DELETE_MENU_OPTION)
