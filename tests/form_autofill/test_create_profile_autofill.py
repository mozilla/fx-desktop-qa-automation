from time import sleep

from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object_navigation import Navigation
from modules.page_object import AboutPrefs
from modules.util import BrowserActions, Utilities


def test_create_address_profile(driver: Firefox, screenshot):
    """
    C122348, creating an address profile
    """
    nav = Navigation(driver)
    about_prefs_obj = AboutPrefs(driver, category="privacy")
    util = Utilities()
    browser_action_obj = BrowserActions(driver)

    nav.open()
    about_prefs_obj.open()

    # create sample data
    autofill_sample_data = util.fake_autofill_data("CA")
    iframe_address_popup = about_prefs_obj.press_button_get_popup_dialog_iframe(
        "Saved addresses"
    )
    browser_action_obj.switch_to_iframe_context(iframe_address_popup)
    about_prefs_obj.get_element(
        "panel-popup-button", labels=["autofill-manage-add-button"]
    ).click()
    about_prefs_obj.fill_autofill_panel_information(autofill_sample_data)

    saved_address_option = about_prefs_obj.get_element("saved-addresses")

    inner_content = saved_address_option.get_attribute("innerHTML")
    print(inner_content)
    cleaned_data = about_prefs_obj.extract_content_from_html(inner_content)
    split_text = about_prefs_obj.extract_and_split_text(cleaned_data)
    print(split_text)
    print(autofill_sample_data)

    # with driver.context(driver.CONTEXT_CHROME):
    #     about_prefs_obj.expect(
    #         EC.presence_of_element_located(
    #             about_prefs_obj.get_selector("element")
    #         )
    #     )
    #     iframe_2 = about_prefs_obj.get_element("browser-popup-2")
    #     print(iframe_2.get_attribute("outerHTML"))
    #     print(iframe_2.get_attribute("innerHTML"))
    # util.write_html_content("second_iframe_inside_iframe", driver, False)
    # util.write_html_content("second_iframe_inside_iframe_chrome", driver, True)
    # screenshot("iframepanelplease")

    # util.write_html_content("iframe1_no_iframe_context", driver, False)
    # util.write_html_content("iframe1_chrome_no_iframe_context", driver, True)

    # browser_action_obj.switch_to_iframe_context(about_prefs_obj.get_element("browser-popup-2"))
    # with driver.context(driver.CONTEXT_CHROME):
    #     # iframe_2 = about_prefs_obj.get_element("browser-popup-2")
    #     # browser_action_obj.switch_to_iframe_context(iframe_2)
    #     about_prefs_obj.expect(EC.frame_to_be_available_and_switch_to_it(
    #         about_prefs_obj.get_selector("browser-popup-2")
    #     ))

    # browser_action_obj.switch_to_iframe_context()
    # EC.frame_to_be_available_and_switch_to_it(
    #     about_prefs_obj.get_selector("browser-popup")
    # )
    # about_prefs_obj.get_element("element")
    # print(iframe_2.get_attribute('outerHTML'))

    # util.write_html_content("iframe1_no_iframe_context", driver, False)
    # util.write_html_content("iframe1_chrome_no_iframe_context", driver, True)

    # browser_action_obj.switch_to_content_context()
    # EC.frame_to_be_available_and_switch_to_it(
    #     about_prefs_obj.get_selector("browser-popup-2")
    # )
    # iframe_address_form_popup = about_prefs_obj.get_element("browser-popup-2")
    # browser_action_obj.switch_to_iframe_context(iframe_address_form_popup)

    # about_prefs_obj.get_element("element")
