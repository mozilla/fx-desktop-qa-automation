from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from modules.browser_object import FindToolbar
from modules.util import BrowserActions

# The number of colors that can be different between two images
# before we call them different color schemes
TOLERANCE = 3


def compare(a: int, b: int) -> bool:
    return abs(a - b) < TOLERANCE


def test_find_toolbar_navigation(driver: Firefox):
    """
    C127249: Navigate through found items
    """
    driver.get("about:about")
    ba = BrowserActions(driver)

    find_toolbar = FindToolbar(driver).open()
    find_toolbar.find("pro")
    match_status = find_toolbar.get_match_args()
    assert match_status["total"] == 4

    # Sometimes we get a match that isn't the first
    # (This also tests that the number is correct)
    while match_status["current"] != 1:
        find_toolbar.previous_match()
        match_status = find_toolbar.get_match_args()

    # Ensure that first match is highlighted, others are not
    processes_selector = (By.CSS_SELECTOR, "a[href='about:processes']")
    protections_selector = (By.CSS_SELECTOR, "a[href='about:protections']")

    processes_colors = ba.get_all_colors_in_element(processes_selector)
    protections_colors = ba.get_all_colors_in_element(protections_selector)

    assert len(processes_colors) > len(protections_colors)
    assert not compare(len(processes_colors), len(protections_colors))

    # Navigate with keyboard and button
    with find_toolbar.driver.context(find_toolbar.driver.CONTEXT_CHROME):
        for _ in range(2):
            find_toolbar.get_element("find-toolbar-input").send_keys(Keys.ENTER)

    find_toolbar.next_match()

    # Now the highlight should be on the other match
    processes_selector = (By.CSS_SELECTOR, "a[href='about:processes']")
    protections_selector = (By.CSS_SELECTOR, "a[href='about:protections']")

    processes_colors = ba.get_all_colors_in_element(processes_selector)
    protections_colors = ba.get_all_colors_in_element(protections_selector)

    assert len(processes_colors) < len(protections_colors)
    assert not compare(len(processes_colors), len(protections_colors))

    # Check what happens when you go past the last match
    find_toolbar.next_match()
    find_toolbar.element_visible("reached-bottom-label")

    # ...And hit Previous on the first match
    find_toolbar.previous_match()
    find_toolbar.element_visible("reached-top-label")
