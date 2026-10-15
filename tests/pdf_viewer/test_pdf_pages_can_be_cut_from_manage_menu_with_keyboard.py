import pytest
from selenium.webdriver.common.keys import Keys

from modules.page_object import GenericPdf

# Cutting pages 1 and 2 renumbers the remaining pages in the sidebar, so the
# original page 4 becomes page 2. Pasting after it puts the cut pages at 3 and 4.
PASTE_AFTER_PAGE = 2

# Unique text on pages 1 and 2 of boeing_brochure.pdf, used to verify that the
# cut pages were pasted into their new position in the page view.
PAGE_ONE_TEXT = "industrialauctioneers"
PAGE_TWO_TEXT = "BOEING TORONTO"


@pytest.fixture()
def test_case():
    return "3969278"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def add_to_prefs_list():
    return [
        # Page checkboxes and the Manage menu only exist with split/merge enabled
        ("pdfjs.enableSplitMerge", True),
        # Lets Tab reach every control on macOS, which skips buttons by default
        ("accessibility.tabfocus", 7),
    ]


def test_pdf_pages_can_be_cut_from_manage_menu_with_keyboard(pdf_viewer: GenericPdf):
    """C3969278: [A11y] Verify that the user can access the "Cut" option from the "Manage" dropdown using keyboard navigation."""
    # The pdf_viewer fixture opens boeing_brochure.pdf

    # Tab to "Manage pages" > Enter to open the Pages sidebar
    pdf_viewer.open_manage_pages_sidebar_with_keyboard()

    # Tab to the page 1 checkbox > Down + Space ticks page 2 > Up + Space ticks page 1 to ensure directions tested
    pdf_viewer.focus_page_checkbox_with_keyboard(1)
    pdf_viewer.select_adjacent_page_with_keyboard(Keys.DOWN, 2)
    pdf_viewer.select_adjacent_page_with_keyboard(Keys.UP, 1)
    pdf_viewer.element_does_not_have_attribute("manage-cut-option", "disabled")

    # Shift+Tab to "Manage" > Enter > Down to "Cut" > Enter
    pdf_viewer.cut_selected_pages_via_manage_menu_with_keyboard()
    pdf_viewer.element_visible(
        "paste-after-page-button", labels=[str(PASTE_AFTER_PAGE)]
    )

    # Tab to "Paste" > Enter, the cut pages should now be pages 3 and 4
    pdf_viewer.paste_pages_after_page_with_keyboard(PASTE_AFTER_PAGE)

    # Check the main page view for the unique text of the cut pages
    pdf_viewer.expect_text_on_page(3, PAGE_ONE_TEXT)
    pdf_viewer.expect_text_on_page(4, PAGE_TWO_TEXT)
