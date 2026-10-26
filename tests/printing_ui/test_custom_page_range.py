from pathlib import Path

import pytest
from auto_fxui.browser_object import PrintPreview
from selenium.webdriver import Firefox


@pytest.fixture()
def test_case():
    return "965146"


FIXTURE = Path("data/pages/print_non_contiguous_ranges.html").resolve()


def test_custom_print_pages(driver: Firefox, print_preview: PrintPreview):
    """C965146 - Verify that custom pages can be selected."""
    driver.get(FIXTURE.as_uri())
    print_preview.open_with_key_combo()
    print_preview.wait_for_preview_ready()

    print_preview.select_page_range("custom")
    assert print_preview.custom_page_range_is_visible()

    print_preview.select_page_range("all")
    assert not print_preview.custom_page_range_is_visible()
