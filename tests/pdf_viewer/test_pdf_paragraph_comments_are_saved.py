import pytest
from selenium.webdriver.common.keys import Keys

from modules.page_object import GenericPdf

ORIGINAL_COMMENT = "Original paragraph comment"
EDITED_COMMENT = "Edited paragraph comment"
KEPT_COMMENT = "Second paragraph comment"
DELETED_COMMENT = "Third paragraph comment to delete"
PARAGRAPHS = (
    "START HERE: Employers must ensure",
    "Employees must complete",
    "All employees can choose",
)


@pytest.fixture()
def test_case():
    return "3139289"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return "i-9.pdf"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("pdfjs.annotationEditorMode", 0),
        ("dom.disable_beforeunload", True),
    ]


def test_pdf_paragraph_comments_are_saved(
    pdf_viewer: GenericPdf, tmp_path, wait_for_file_download
):
    """C3139289: Edited and deleted paragraph comments persist in a saved PDF."""
    # Step 1: The fixture opens the local PDF.
    # Steps 2 and 4: Add the first comment, then two more on distinct paragraphs.
    highlights = []
    for paragraph_text, comment in zip(
        PARAGRAPHS, (ORIGINAL_COMMENT, KEPT_COMMENT, DELETED_COMMENT)
    ):
        paragraph = pdf_viewer.get_element(
            "pdf-text-containing", labels=[paragraph_text]
        )
        pdf_viewer.element_visible(paragraph)
        pdf_viewer.highlight_pdf_text(paragraph)
        new_highlights = [
            highlight
            for highlight in pdf_viewer.get_elements("added-highlight")
            if highlight not in highlights
        ]
        assert len(new_highlights) == 1
        highlights.extend(new_highlights)
        pdf_viewer.add_comment_to_selected_highlight(comment)
        pdf_viewer.click_on("toolbar-highlight")
        # Step 3: Edit the first comment before adding the two additional comments.
        if comment == ORIGINAL_COMMENT:
            pdf_viewer.click_on("comment-indicator")
            pdf_viewer.element_visible("comment-popup-text")
            assert pdf_viewer.get_element("comment-popup-text").text == ORIGINAL_COMMENT
            pdf_viewer.click_on("comment-popup-edit")
            pdf_viewer.element_visible("comment-dialog")
            pdf_viewer.fill("comment-input", EDITED_COMMENT, press_enter=False)
            pdf_viewer.click_on("comment-save")
            pdf_viewer.element_not_visible("comment-dialog")

    # Step 4: Find the comment to remove by text; indicators follow page order.
    for indicator in pdf_viewer.get_elements("comment-indicator"):
        indicator.click()
        pdf_viewer.element_visible("comment-popup-text")
        if pdf_viewer.get_element("comment-popup-text").text == DELETED_COMMENT:
            break
        pdf_viewer.perform_key_combo(Keys.ESCAPE)
        pdf_viewer.element_not_visible("comment-popup-text")
    else:
        pytest.fail("The comment to delete was not found.")
    # Delete only the comment and confirm all three paragraph highlights remain.
    pdf_viewer.click_on("comment-popup-delete")
    pdf_viewer.element_not_visible("comment-popup-text")
    assert len(pdf_viewer.get_elements("comment-indicator")) == 2
    assert set(pdf_viewer.get_elements("added-highlight")) == set(highlights)

    # Record the surviving comments and their positions to check their saved links.
    original_positions = {}
    for indicator in pdf_viewer.get_elements("comment-indicator"):
        indicator.click()
        pdf_viewer.element_visible("comment-popup-text")
        original_positions[pdf_viewer.get_element("comment-popup-text").text] = (
            indicator.rect
        )
        pdf_viewer.perform_key_combo(Keys.ESCAPE)
        pdf_viewer.element_not_visible("comment-popup-text")

    # Step 5: Save a separate copy using the mock picker instead of the native dialog.
    saved_pdf = tmp_path / "saved-paragraph-comments.pdf"
    pdf_viewer.install_mock_file_picker(str(saved_pdf))
    try:
        pdf_viewer.click_download_button()
        pdf_viewer.wait_for_mock_file_picker()
    finally:
        pdf_viewer.cleanup_mock_file_picker()
    wait_for_file_download(saved_pdf)

    # Step 6: Reopen the saved PDF in Firefox and verify the comments and their links.
    saved_viewer = GenericPdf(pdf_viewer.driver, pdf_url=saved_pdf.as_uri())
    saved_viewer.expect(
        lambda _: len(saved_viewer.get_elements("comment-indicator")) == 2
    )
    comments = []
    for indicator in saved_viewer.get_elements("comment-indicator"):
        indicator.click()
        saved_viewer.element_visible("comment-popup-text")
        comment = saved_viewer.get_element("comment-popup-text").text
        comments.append(comment)
        assert comment in original_positions
        # Saved annotations can shift the comment icon by a couple of CSS pixels.
        assert indicator.rect == pytest.approx(original_positions[comment], abs=2), (
            "The saved comment should remain linked to the same paragraph."
        )
        saved_viewer.perform_key_combo(Keys.ESCAPE)
        saved_viewer.element_not_visible("comment-popup-text")
    # Only the edited and retained comments should survive; the deleted one must not.
    assert sorted(comments) == sorted([EDITED_COMMENT, KEPT_COMMENT])
