from pathlib import Path
import pytest
from auto_fxui.page_object import GenericPdf

PDF_FIXTURE = Path(__file__).resolve().parents[2] / "data" / "i-9.pdf"
PDF_URL = PDF_FIXTURE.as_uri()


@pytest.fixture()
def test_case():
    return "3969302"


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.enableSplitMerge", True)]


@pytest.fixture()
def pdf_viewer(driver):
    return GenericPdf(driver, pdf_url=PDF_URL)


@pytest.mark.parametrize(
    "selected_pages",
    [
        [1],
        [1, 2],
        [1, 3],
    ],
    ids=["single_page", "consecutive_pages", "non_consecutive_pages"],
)
def test_pdf_new_badge_state_during_page_selection(
    pdf_viewer: GenericPdf, selected_pages: list[int]
):
    """
    C3969302 - Verify the "NEW" green badge state during page selection.
    """
    # Step 1: Load a PDF document.
    pdf_viewer.element_visible("pdf-body")

    # Step 2: Activate Pages from sidebar.
    pdf_viewer.click_on("pages-sidebar-toggle")
    pdf_viewer.element_visible("page-thumbnail-checkbox", labels=["1"])

    # Verify that before selecting pages, the "NEW" green badge is visible.
    pdf_viewer.element_visible("views-manager-new-badge")

    # Step 3: Select one or multiple (consecutive and non-consecutive) pages.
    if hasattr(pdf_viewer, "select_pdf_pages"):
        pdf_viewer.select_pdf_pages(selected_pages)
    else:
        for page in selected_pages:
            pdf_viewer.click_on("page-thumbnail-checkbox", labels=[str(page)])

    # Expected: After selecting pages the "NEW" green badge should disappear.
    pdf_viewer.element_not_visible("views-manager-new-badge")

    # Step 4: Click on "Mass deselect" checkbox/button.
    pdf_viewer.mass_deselect_pages()

    # Expected: The "NEW" green badge reappears.
    pdf_viewer.element_visible("views-manager-new-badge")