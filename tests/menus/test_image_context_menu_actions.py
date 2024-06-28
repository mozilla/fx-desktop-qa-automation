import platform
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ImageContextMenu, Navigation, TabBar
from modules.page_object import WikiFirefoxLogo
from modules.util import BrowserActions, Utilities


def test_open_image_in_new_tab(driver: Firefox):
    """
    C2637622.1: open an image in a new tab
    """
    # create objs
    wiki_image_page = WikiFirefoxLogo(driver).open()
    image_context_menu = ImageContextMenu(driver)
    tabs = TabBar(driver)

    # wait for page to load
    wiki_image_page.wait_for_page_to_load()

    # get the image and context click it
    image_logo = wiki_image_page.get_image()
    wiki_image_page.context_click_element(image_logo)

    # open in a new tab
    open_in_new_tab = image_context_menu.get_context_item(
        "context-menu-open-image-in-new-tab"
    )
    image_context_menu.click_context_item(open_in_new_tab)
    wiki_image_page.hide_popup_by_child_node(open_in_new_tab, chrome=True)

    # switch to the second tab and verify the URL
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[1])
    wiki_image_page.wait_for_page_to_load()
    wiki_image_page.verify_opened_image_url()


@pytest.mark.unstable
def test_save_image_as(driver: Firefox):
    """
    C2637622.2: save image as
    """
    try:
        from pynput.keyboard import Key
    except ModuleNotFoundError:
        pytest.skip("Could not load pynput")

    wiki_image_page = WikiFirefoxLogo(driver).open()
    image_context_menu = ImageContextMenu(driver)
    nav = Navigation(driver)
    ba = BrowserActions(driver)
    util = Utilities()

    # wait for page to load
    wiki_image_page.wait_for_page_to_load()

    # get the image and context click it
    image_logo = wiki_image_page.get_image()
    wiki_image_page.context_click_element(image_logo)

    # save it
    save_image_as = image_context_menu.get_context_item("context-menu-save-image-as")
    image_context_menu.click_context_item(save_image_as)
    wiki_image_page.hide_popup_by_child_node(save_image_as, chrome=True)

    # create the pynput controller
    downloads_button = nav.get_download_button()

    # wait some time before interacting with the system dialog
    sleep(0.5)

    this_platform = platform.system()
    if this_platform == "Linux":
        ba.controller.press(Key.alt)
        ba.controller.press(Key.tab)
        ba.controller.release(Key.tab)
        ba.controller.release(Key.alt)

        ba.controller.press(Key.alt)
        ba.controller.press(Key.tab)
        ba.controller.release(Key.tab)
        ba.controller.release(Key.alt)

        ba.key_press_release(Key.tab)

        ba.key_press_release(Key.tab)

    # Press and release the Enter key
    ba.key_press_release(Key.enter)

    # Wait for the animation to complete
    nav.wait_for_download_animation_finish(downloads_button)

    saved_image_location = util.get_saved_file_path("Firefox_logo,_2019.svg.png")

    util.check_file_path_validility(saved_image_location)

    util.remove_file(saved_image_location)


def test_copy_image_link(driver: Firefox):
    """
    C2637622.3: copy an image link and verify its correct
    """
    # create objs
    nav = Navigation(driver).open()
    wiki_image_page = WikiFirefoxLogo(driver).open()
    image_context_menu = ImageContextMenu(driver)
    tabs = TabBar(driver)

    # wait for page to load
    wiki_image_page.wait_for_page_to_load()

    # get the image and context click it
    image_logo = wiki_image_page.get_image()
    wiki_image_page.context_click_element(image_logo)

    # copy the link
    copy_image_link = image_context_menu.get_context_item(
        "context-menu-copy-image-link"
    )
    image_context_menu.click_context_item(copy_image_link)
    wiki_image_page.hide_popup_by_child_node(copy_image_link, chrome=True)

    # open a new tab
    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[1])

    # # context click and paste
    search_bar = nav.get_awesome_bar()
    nav.context_click_element(search_bar)

    # paste and go
    with driver.context(driver.CONTEXT_CHROME):
        paste_and_go = nav.get_element("context-menu-paste-and-go")
        paste_and_go.click()
        nav.hide_popup_by_child_node(paste_and_go)

    wiki_image_page.wait_for_page_to_load()
    with driver.context(driver.CONTEXT_CONTENT):
        wiki_image_page.verify_opened_image_url()
