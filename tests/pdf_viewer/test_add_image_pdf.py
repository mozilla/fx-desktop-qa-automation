from pathlib import Path

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu
from modules.page_object import GenericPdf

IMAGE_FILE_NAME = "goomy.png"
ADDED_IMAGE_ELEMENT = "added-goomy-image"
DELETE_MENU_OPTION = "pdfjs-delete"

DATA_DIR = Path("data")


@pytest.fixture()
def hard_quit():
    """Overwriting the hard quit fixture in parent conftest.py"""
    return True


@pytest.fixture()
def test_case():
    return "2228202"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.ml.enable", True),
        ("pdfjs.enableAltText", False),
        ("pdfjs.enableUpdatedAddImage", True),
    ]


@pytest.fixture()
def image_path() -> Path:
    """Absolute path to the image file."""
    return (DATA_DIR / IMAGE_FILE_NAME).resolve()


# This test is unstable in Linux (all CI) for now: Bug 1983852
@pytest.mark.headed
@pytest.mark.noxvfb
def test_add_image_pdf(
    driver: Firefox, sys_platform, pdf_viewer: GenericPdf, image_path: Path, hard_quit
):
    """
    C2228202: Verify that the user is able to add an image to a PDF file.

    Arguments:
        sys_platform: Current System Platform Type
        pdf_viewer: Fixture returning instance of GenericPdf with correct path.
        image_path: Absolute path to the image file used in this test.
    """
    context_menu = ContextMenu(driver)

    # Add image
    pdf_viewer.add_image(str(image_path), sys_platform)

    # Verify image is added
    pdf_viewer.element_visible(ADDED_IMAGE_ELEMENT)

    # Right click and delete
    pdf_viewer.context_click(ADDED_IMAGE_ELEMENT)
    context_menu.click_and_hide_menu(DELETE_MENU_OPTION)
