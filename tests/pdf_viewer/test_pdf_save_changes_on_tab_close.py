import pytest
from auto_fxui.browser_object import TabBar
from auto_fxui.page_object import GenericPdf
from selenium.common.exceptions import (NoAlertPresentException,
                                        NoSuchWindowException)


@pytest.fixture()
def test_case():
    return "3969293"


@pytest.fixture()
def firefox_options(firefox_options):
    # Classic WebDriver automatically accepts beforeunload prompts.
    firefox_options.set_capability("webSocketUrl", True)
    firefox_options.set_capability(
        "unhandledPromptBehavior", {"beforeUnload": "ignore"}
    )
    return firefox_options


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("pdfjs.enableSplitMerge", True),
        ("dom.disable_beforeunload", False),
        ("browser.download.useDownloadDir", False),
    ]


def test_pdf_save_changes_on_tab_close(
    pdf_viewer: GenericPdf, tmp_path, wait_for_file_download, sys_platform
):
    """C3969293: Closing an edited PDF offers to save all changes."""
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

    # Step 5: Close the edited tab and verify the save-before-leaving prompt.
    driver = pdf_viewer.driver
    edited_tab = driver.current_window_handle
    driver.switch_to.new_window("tab")
    remaining_tab = driver.current_window_handle
    driver.switch_to.window(edited_tab)
    saved_pdf = tmp_path / "saved-on-close.pdf"
    pdf_viewer.install_mock_file_picker(str(saved_pdf))
    try:
        TabBar(driver).close_tab_shortcut(sys_platform)
        alert = pdf_viewer.get_alert()
        assert "Save this document to avoid losing your changes." == alert.text, (
            "Closing an edited PDF should offer to save before leaving."
        )

        # Step 6: Save the PDF and wait for the edited tab to close.
        alert.accept()
        pdf_viewer.wait.until(
            lambda _: edited_tab not in driver.window_handles,
            message="Saving the edited PDF should allow its tab to close.",
        )
        driver.switch_to.window(remaining_tab)
        pdf_viewer.wait_for_mock_file_picker()
    finally:
        try:
            driver.switch_to.alert.dismiss()
        except (NoAlertPresentException, NoSuchWindowException):
            pass
        if edited_tab not in driver.window_handles:
            driver.switch_to.window(remaining_tab)
        pdf_viewer.cleanup_mock_file_picker()
    wait_for_file_download(saved_pdf)

    # Step 7: Reopen the saved PDF and verify every page and its order.
    saved_viewer = GenericPdf(driver, pdf_url=saved_pdf.as_uri())
    assert saved_viewer.max_page == len(edited_text), (
        "The saved PDF should retain all remaining pages after deletion."
    )
    for number, expected_text in enumerate(edited_text, start=1):
        assert saved_viewer.get_page_text(number) == expected_text, (
            f"Saved page {number} should preserve its edited content and order."
        )
