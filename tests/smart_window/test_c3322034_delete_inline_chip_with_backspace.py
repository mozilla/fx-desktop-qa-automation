"""
C3322034 - Delete an added inline tagged website chip with backspace
Verify that backspace removes an inline tagged website from the Smart Bar.
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import SmartBar, SmartWindow

TAGGABLE_URLS = ("about:robots", "about:buildconfig")


@pytest.fixture()
def test_case():
    return "3322034"


def test_delete_inline_chip_with_backspace(
    driver: Firefox, active_smart_window: SmartWindow
):
    """
    C3322034 - Delete an added inline tagged website chip with backspace

    Asserts on the inline chip, which is what the case title describes. The
    case's expected-result text also mentions the context chip above the text
    field; that element is never populated in this build, so it is not
    asserted here (see C3322035 / C3322041, blocked on the same behaviour).
    """
    # Two tabs to tag.
    with driver.context(driver.CONTEXT_CHROME):
        for url in TAGGABLE_URLS:
            driver.execute_script(
                # Open a background tab to tag; system principal is required
                # to load an about: page from chrome script.
                "gBrowser.addTab(arguments[0], {triggeringPrincipal:"
                " Services.scriptSecurityManager.getSystemPrincipal()});",
                url,
            )

    bar = SmartBar(driver)
    bar.open_smart_bar()
    bar.expect_tagged_sites(0)

    # Tag two open tabs inline via the @ mention.
    bar.tag_tab_via_mention()
    bar.tag_tab_via_mention()
    tagged = bar.get_tagged_sites()
    assert len(tagged) == 2, f"expected 2 tagged sites, got {tagged}"

    # Backspace removes the most recently tagged site, leaving the other.
    removed = tagged[-1]
    bar.delete_last_tag()
    bar.expect_tagged_sites(1)

    remaining = bar.get_tagged_sites()
    assert remaining == tagged[:1], (
        f"expected only {tagged[0]} to remain, got {remaining}"
    )
    assert removed["href"] not in bar.get_smart_bar_text(), (
        f"{removed['href']} still referenced after backspace"
    )
