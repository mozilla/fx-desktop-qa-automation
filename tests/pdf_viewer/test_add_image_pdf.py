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
    """Ensure the browser session is force-quit after the test run."""
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


@pytest.fixture()
def context_menu(driver: Firefox) -> ContextMenu:
    """Context menu browser object model."""
    return ContextMenu(driver)


# This test is unstable in Linux (all CI) for now: Bug 1983852
@pytest.mark.headed
@pytest.mark.noxvfb
def test_add_image_pdf(
    driver: Firefox,
    sys_platform,
    pdf_viewer: GenericPdf,
    context_menu: ContextMenu,
    image_path: Path,
):
    """
    C2228202: Verify that the user is able to add an image to a PDF file.

    Arguments:
        sys_platform: Current System Platform Type
        pdf_viewer: Instance of GenericPdf with correct path.
        context_menu: Context menu object model.
        image_path: Absolute path to the image file used in this test.
    """
    # Add image
    pdf_viewer.add_image(str(image_path), sys_platform)

    # Verify image is added
    pdf_viewer.element_visible(ADDED_IMAGE_ELEMENT)

    # Right click and delete
    pdf_viewer.context_click(ADDED_IMAGE_ELEMENT)
    context_menu.click_and_hide_menu(DELETE_MENU_OPTION)
