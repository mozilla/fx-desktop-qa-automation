import pytest
from auto_fxui.page_object import GenericPdf


@pytest.fixture()
def test_case():
    return "3969294"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("pdfjs.enableSplitMerge", True),
        ("dom.disable_beforeunload", True),
        ("browser.download.useDownloadDir", False),
    ]


def test_pdf_global_save_changes(
    pdf_viewer: GenericPdf, tmp_path, wait_for_file_download
):
    """C3969294: The global Save button preserves all PDF edits."""
    # Step 1: Open the local PDF and record distinct source-page content.
    original_count = pdf_viewer.max_page
    assert original_count >= 4, "The source PDF should contain at least four pages."
    original_text = [
        pdf_viewer.get_page_text(number) for number in range(1, original_count + 1)
    ]
    assert len(set(original_text)) == original_count, (
        "Source pages should have distinct text to detect an incorrect saved order."
    )
    pdf_viewer.jump_to_page(1)

    # Step 2: Open Pages and retain the original thumbnail identities.
    pdf_viewer.click_on("pages-sidebar-toggle")
    original_pages = pdf_viewer.get_elements("page-thumbnails")
    assert len(original_pages) == original_count, (
        "The sidebar should show every source page."
    )

    # Step 3: Drag the first page after the second and verify the new order.
    pdf_viewer.select_pdf_pages([1])
    pdf_viewer.drag_page_after(1, 2)
    reordered_pages = [original_pages[1], original_pages[0], *original_pages[2:]]
    pdf_viewer.wait.until(
        lambda _: pdf_viewer.get_elements("page-thumbnails") == reordered_pages,
        message="Dragging should put original page one after original page two.",
    )

    # Step 4: Delete the last page and verify the remaining reordered content.
    pdf_viewer.select_pdf_pages([original_count])
    pdf_viewer.click_on("manage-dropdown-button")
    pdf_viewer.click_on("manage-delete-option")
    pdf_viewer.wait.until(
        lambda _: pdf_viewer.get_elements("page-thumbnails") == reordered_pages[:-1],
        message="Deleting the last page should preserve the remaining page order.",
    )
    edited_text = [
        original_text[1],
        original_text[0],
        *original_text[2:-1],
    ]
    for number, expected_text in enumerate(edited_text, start=1):
        assert pdf_viewer.get_page_text(number) == expected_text, (
            f"Edited page {number} should contain the expected source-page text."
        )

    # Steps 5-6: Use global Save and accept the file picker at a temporary path.
    saved_pdf = tmp_path / "global-save-edited.pdf"
    pdf_viewer.install_mock_file_picker(str(saved_pdf))
    try:
        pdf_viewer.click_download_button()
        pdf_viewer.wait_for_mock_file_picker()
    finally:
        pdf_viewer.cleanup_mock_file_picker()
    wait_for_file_download(saved_pdf)

    # Step 7: Reopen in a new tab and verify every remaining page and its order.
    pdf_viewer.driver.switch_to.new_window("tab")
    saved_viewer = GenericPdf(pdf_viewer.driver, pdf_url=saved_pdf.as_uri())
    assert saved_viewer.max_page == len(edited_text), (
        "Global Save should retain every remaining page and exclude the deleted page."
    )
    for number, expected_text in enumerate(edited_text, start=1):
        assert saved_viewer.get_page_text(number) == expected_text, (
            f"Globally saved page {number} should preserve its edited content and order."
        )
