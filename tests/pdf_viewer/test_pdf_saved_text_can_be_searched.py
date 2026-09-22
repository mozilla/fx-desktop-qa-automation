from pathlib import Path

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import FindToolbar
from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"
DOWNLOADED_PDF_NAME = "i-9-searchable-text.pdf"
SEARCH_TEXT = "QA PDF text 1938272"


@pytest.fixture()
def test_case():
    return "1938272"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("pdfjs.annotationEditorMode", 0),
        ("dom.disable_beforeunload", True),
    ]


def test_pdf_saved_text_can_be_searched(
    driver: Firefox,
    pdf_viewer: GenericPdf,
    tmp_path: Path,
    wait_for_file_download,
):
    """C1938272: Text added to a saved PDF can be found with Ctrl/Cmd+F."""
    saved_pdf_path = (tmp_path / DOWNLOADED_PDF_NAME).resolve()

    pdf_viewer.element_visible("toolbar-text")
    pdf_viewer.element_visible("toolbar-draw")
    pdf_viewer.select_editor_tool("toolbar-text")
    pdf_viewer.add_text_to_pdf_page(SEARCH_TEXT)
    pdf_viewer.select_pdf_text_area()

    pdf_viewer.install_mock_file_picker(str(saved_pdf_path))
    try:
        pdf_viewer.click_download_button()
        pdf_viewer.wait_for_mock_file_picker()
    finally:
        pdf_viewer.cleanup_mock_file_picker()

    assert wait_for_file_download(saved_pdf_path), (
        f"Expected saved PDF at {saved_pdf_path}."
    )

    saved_pdf_viewer = GenericPdf(driver, pdf_url=saved_pdf_path.as_uri())
    saved_pdf_viewer.wait_for_saved_text(SEARCH_TEXT)

    find_toolbar = FindToolbar(driver)
    find_toolbar.open_with_key_combo()
    find_toolbar.find(SEARCH_TEXT)
    assert find_toolbar.match_dict.get("total", 0) == 1, (
        f"Expected one match for '{SEARCH_TEXT}', got {find_toolbar.match_dict}."
    )
