import re

import pytest
from selenium.webdriver.support.color import Color

from auto_fxui.page_object import GenericPdf


@pytest.fixture()
def test_case():
    return "3969288"


@pytest.fixture()
def file_name():
    return "i-9.pdf"


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.enableSplitMerge", True), ("dom.disable_beforeunload", True)]


@pytest.mark.parametrize(
    "selected_numbers, target_number, before",
    [((2, 3), 1, True), ((1, 3), 2, False)],
    ids=["consecutive", "nonconsecutive"],
)
def test_pdf_multiple_page_drag(
    pdf_viewer: GenericPdf,
    tmp_path,
    wait_for_file_download,
    selected_numbers,
    target_number,
    before,
):
    """C3969288: Reorder selected pages together and preserve them in a saved PDF."""
    # Step 1: Open the local PDF and record each page's rendered content.
    assert pdf_viewer.max_page >= 3, (
        "Multiple-page dragging needs at least three pages."
    )
    original_text = [
        pdf_viewer.get_page_text(number) for number in range(1, pdf_viewer.max_page + 1)
    ]
    assert len(set(original_text)) == len(original_text), (
        "Each source page must have distinct text to detect incorrect page order."
    )
    pdf_viewer.jump_to_page(1)

    # Step 2: Open Pages and retain the original thumbnail identities.
    pdf_viewer.click_on("pages-sidebar-toggle")
    original_pages = pdf_viewer.get_elements("page-thumbnails")

    # Step 3: Check the consecutive or nonconsecutive pages.
    selected_checkboxes = []
    for number in selected_numbers:
        pdf_viewer.click_on("page-thumbnail-checkbox", labels=[str(number)])
        selected_checkboxes.append(
            pdf_viewer.get_element("page-thumbnail-checkbox", labels=[str(number)])
        )
    assert pdf_viewer.get_elements("selected-page-checkboxes") == selected_checkboxes, (
        "Only the requested pages should be checked."
    )
    sources = [
        pdf_viewer.get_element("page-thumbnail-image", labels=[str(number)])
        for number in selected_numbers
    ]
    target = pdf_viewer.get_element("page-thumbnail-image", labels=[str(target_number)])
    source_rects = [source.rect for source in sources]

    # Step 4: Hold the selected group at the drop location and check its feedback.
    try:
        pdf_viewer.actions.move_to_element(sources[0]).click_and_hold().move_by_offset(
            0, 15
        ).perform()
        offset = int(target.size["height"] / 2) + 15
        pdf_viewer.actions.move_to_element_with_offset(
            target, 0, -offset if before else offset
        ).perform()
        pdf_viewer.element_visible("page-drag-placeholder")
        placeholders = pdf_viewer.get_elements("page-drag-placeholder")
        assert len(placeholders) == len(sources), (
            "A placeholder should remain for every dragged page."
        )
        for placeholder, rect in zip(placeholders, source_rects):
            assert placeholder.rect == pytest.approx(rect, abs=2), (
                "Each placeholder should remain at its selected page's original position."
            )
        pdf_viewer.element_visible("page-drop-guide")
        guide = pdf_viewer.get_element("page-drop-guide")
        color = Color.from_string(guide.value_of_css_property("border-top-color"))
        assert color.blue > color.red, "The drop guide should be blue."
        assert (
            float(guide.value_of_css_property("border-top-width").removesuffix("px"))
            > 0
        ), "The drop guide should have a visible border."
        if before:
            assert guide.rect["y"] <= target.rect["y"], (
                "The guide should indicate a drop before the target page."
            )
        else:
            assert guide.rect["y"] >= target.rect["y"] + target.rect["height"], (
                "The guide should indicate a drop after the target page."
            )
        group = pdf_viewer.get_element("dragged-page-group")
        assert group.get_attribute("data-multiple-count") == str(len(sources)), (
            "The drag preview should represent every selected page."
        )
        colors = re.findall(
            r"rgba?\([^)]+\)", group.value_of_css_property("box-shadow")
        )
        assert any(
            Color.from_string(value).blue > Color.from_string(value).red
            for value in colors
        ), "The dragged page group should have a blue highlight."
    finally:
        pdf_viewer.actions.release().perform()

    order = [
        number
        for number in range(1, len(original_pages) + 1)
        if number not in selected_numbers
    ]
    insertion = order.index(target_number) + (not before)
    order[insertion:insertion] = selected_numbers
    expected_pages = [original_pages[number - 1] for number in order]
    pdf_viewer.wait.until(
        lambda _: pdf_viewer.get_elements("page-thumbnails") == expected_pages,
        message="Selected pages should move together in their original relative order.",
    )
    assert [page.get_attribute("page-number") for page in expected_pages] == [
        str(number) for number in range(1, len(expected_pages) + 1)
    ], "The reordered thumbnails should be numbered consecutively."
    assert pdf_viewer.get_elements("focused-page-thumbnail") == [
        original_pages[selected_numbers[0] - 1]
    ], "Focus should remain on the first selected page."
    pdf_viewer.element_not_visible("page-drag-placeholder")
    pdf_viewer.element_not_visible("page-drop-guide")

    # Step 5: Reselect the moved pages, copy through Manage, and paste after the last page.
    selected_checkboxes = []
    for original_number in selected_numbers:
        checkbox = pdf_viewer.get_element(
            "page-thumbnail-checkbox", labels=[str(order.index(original_number) + 1)]
        )
        if not checkbox.is_selected():
            pdf_viewer.click_on(checkbox)
        selected_checkboxes.append(checkbox)
    assert pdf_viewer.get_elements("selected-page-checkboxes") == selected_checkboxes, (
        "Manage should act on exactly the pages that were dragged."
    )
    pdf_viewer.click_on("manage-dropdown-button")
    pdf_viewer.click_on("manage-copy-option")
    pdf_viewer.click_on("paste-after-page-button", labels=[str(len(original_pages))])
    order.extend(selected_numbers)
    pdf_viewer.expect(
        lambda _: len(pdf_viewer.get_elements("page-thumbnails")) == len(order)
    )
    assert [
        page.get_attribute("page-number")
        for page in pdf_viewer.get_elements("page-thumbnails")
    ] == [str(number) for number in range(1, len(order) + 1)], (
        "Copied pages should be added and all thumbnails renumbered consecutively."
    )
    for number, original_number in enumerate(order, start=1):
        assert pdf_viewer.get_page_text(number) == original_text[original_number - 1], (
            f"Page {number} should contain original page {original_number} after copying."
        )

    # Step 6: Save the entire modified PDF using the toolbar Save button.
    saved_pdf = tmp_path / "reordered-pages.pdf"
    pdf_viewer.install_mock_file_picker(str(saved_pdf))
    try:
        pdf_viewer.click_download_button()
        pdf_viewer.wait_for_mock_file_picker()
    finally:
        pdf_viewer.cleanup_mock_file_picker()
    wait_for_file_download(saved_pdf)

    # Step 7: Reopen in a new tab and verify the complete saved order and copies.
    pdf_viewer.driver.switch_to.new_window("tab")
    saved_viewer = GenericPdf(pdf_viewer.driver, pdf_url=saved_pdf.as_uri())
    assert saved_viewer.max_page == len(order), (
        "The saved PDF should include every copied page."
    )
    for number, original_number in enumerate(order, start=1):
        assert (
            saved_viewer.get_page_text(number) == original_text[original_number - 1]
        ), f"Saved page {number} should contain original page {original_number}."
