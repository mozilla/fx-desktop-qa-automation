from pynput.keyboard import Key

from modules.page_base import BasePage
from modules.util import BrowserActions, Utilities


class AboutProfiles(BasePage):
    """
    POM for about:profiles page
    """

    URL_TEMPLATE = "about:profiles"
