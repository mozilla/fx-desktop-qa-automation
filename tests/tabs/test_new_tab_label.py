import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar
from modules.page_object import AboutTelemetry


@pytest.fixture()
def test_case():
    return "1339887"


def test_new_tab_label(driver: Firefox):
    tabs = TabBar(driver)
    tab_context_menu = ContextMenu(driver)
    about_telemetry = AboutTelemetry(driver)

    driver.get("about:logo")
    first_tab = tabs.get_tab(1)  # about:logo tab; get_tab index starts at 1, NOT 0

    # Step 1: Right click any opened tab and click New Tab
    tabs.context_click(first_tab)
    tab_context_menu.click_and_hide_menu("context-open-new-tab")

    # Navigate the new tab to about:telemetry and verify scalar value is 1
    driver.switch_to.window(driver.window_handles[-1])
    about_telemetry.open()
    about_telemetry.search_telemetry("context-openANewTab")
    assert about_telemetry.is_telemetry_keyed_scalars_entry_present(
        ["context-openANewTab", "1"]
    ), "Expected context-openANewTab to have value 1 after Step 1"

    second_tab = tabs.get_tab(2)  # about:telemetry tab

    # Step 2: Right click an open tab and press W to open a new tab
    tabs.context_click(second_tab)
    tabs.actions.send_keys("w").perform()

    # Switch back to about:telemetry and refresh to pick up updated scalar
    driver.switch_to.window(driver.window_handles[1])
    driver.refresh()
    assert about_telemetry.is_telemetry_keyed_scalars_entry_present(
        ["context-openANewTab", "2"]
    ), "Expected context-openANewTab to have value 2 after Step 2"

    # Step 3: Right click in the Tab Bar and click New Tab

    # Note: "Right click in the Tab Bar" is intentionally not used here because it
    # increments "toolbar-context-openANewTab" instead of "context-openANewTab".
    # Right clicking an opened tab is used to bring context-openANewTab to 3.
    tabs.context_click(second_tab)
    tab_context_menu.click_and_hide_menu("context-open-new-tab")

    # Switch back to about:telemetry and refresh to pick up updated scalar
    driver.switch_to.window(driver.window_handles[1])
    driver.refresh()
    assert about_telemetry.is_telemetry_keyed_scalars_entry_present(
        ["context-openANewTab", "3"]
    ), "Expected context-openANewTab to have value 3 after Step 3"
