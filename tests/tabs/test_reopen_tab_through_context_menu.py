from selenium.webdriver import Firefox

from modules.browser_object import TabBar, TabContextMenu


def test_reopen_tab_through_context_menu(driver: Firefox):
    """C134648: Reopen tab through context menu"""
    tabs = TabBar(driver).open()
    tab_context_menu = TabContextMenu(driver)

    tabs_to_open = 4

    driver.get("about:about")
    for _ in range(1, tabs_to_open):
        tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[-1])
    driver.get("about:robots")
    remaining_tab = tabs.get_tab(1)
    closing_tab = tabs.get_tab(tabs_to_open)

    with driver.context(driver.CONTEXT_CHROME):
        assert tabs.get_tab_title(closing_tab).startswith("Gort")

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    with driver.context(driver.CONTEXT_CHROME):
        tabs.actions.context_click(remaining_tab).perform()
        reopen_item = tab_context_menu.get_context_item("context-menu-reopen-tab")
        reopen_item.click()

        # tab numbers are not reused, so the reopened tab is 1 higher
        reopened_tab = tabs.get_tab(tabs_to_open + 1)
        assert tabs.get_tab_title(reopened_tab).startswith("Gort")

        tabs.hide_popup("tabContextMenu")
