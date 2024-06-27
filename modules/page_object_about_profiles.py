import platform
from time import sleep

from pynput.keyboard import Key
from selenium.common import NoAlertPresentException

from modules.page_base import BasePage
from modules.util import BrowserActions, Utilities


class AboutProfiles(BasePage):
    """
    POM for about:profiles page
    """

    URL_TEMPLATE = "about:profiles"

    def create_new_profile(self, util: Utilities, ba: BrowserActions) -> BasePage:
        """
        Creates a new profile with a random name
        """
        self.get_element("create-profile-button").click()

        profile_name = util.generate_random_text("word")

        current_platform = platform.system()

        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            print(f"Alert detected with message: {alert_text}")
            alert.accept()  # or alert.dismiss()
        except NoAlertPresentException:
            print("No alerts detected.")

        # sleep(0.5)
        # if current_platform == "Linux":
        #     self.system_dialog_interation_linux()
        # elif current_platform == "Windows":
        #     self.system_dialog_interation_windows()
        # else:
        #     print("running")
        #     self.system_dialog_interation_macos(profile_name, ba)
        # sleep(10)

    def system_dialog_interation_linux(self):
        pass

    def system_dialog_interation_macos(self, profile_name: str, ba: BrowserActions):
        ba.key_press_release(Key.tab)
        print("hello")
        ba.key_press_release(Key.enter)
        print("hello")

        ba.controller.type(profile_name)
        print("hello")
        ba.key_press_release(Key.tab)
        print("hello")
        ba.key_press_release(Key.tab)
        print("hello")
        ba.key_press_release(Key.tab)
        print("hello")
        ba.key_press_release(Key.tab)
        print("hello")
        ba.key_press_release(Key.enter)
        print("hello")

    def system_dialog_interation_windows(self):
        pass
