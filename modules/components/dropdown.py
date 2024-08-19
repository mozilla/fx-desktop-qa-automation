from pypom import Region
from modules.util import PomUtils

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class Dropdown(Region):
    """
    PyPOM Region factory for Dropdown menus in about:prefs. See PyPOM docs on Regions.
    """

    def __init__(self, page, require_shadow=True, **kwargs):
        super().__init__(page, **kwargs)
        self.utils = PomUtils(self.page.driver)
        if require_shadow:
            self.shadow_elements = self.utils.get_shadow_content(self.root)
            self.dropmarker = next(
                el for el in self.shadow_elements if el.tag_name == "dropmarker"
            )

    @property
    def loaded(self):
        return self.root if EC.element_to_be_clickable(self.root) else False

    def select_option(
        self,
        option_name: str,
        double_click=False,
        wait_for_selection=True,
        option_tag="menuitem",
        label_name="label",
    ):
        """Select an option in the dropdown. Does not return self."""
        try:
            if not self.dropmarker.get_attribute("open") == "true":
                self.root.click()
        except AttributeError:
            self.root.click()

        matching_menuitems = [
            el
            for el in self.root.find_elements(By.CSS_SELECTOR, option_tag)
            if el.get_attribute(label_name) == option_name
        ]
        if len(matching_menuitems) == 0:
            return False
        elif len(matching_menuitems) == 1:
            if double_click:
                self.page.double_click(
                    reference=matching_menuitems[0]
                )
            else:
                matching_menuitems[0].click()
            if wait_for_selection:
                self.wait.until(EC.element_to_be_selected(matching_menuitems[0]))
            return self
        else:
            raise ValueError("More than one menu item matched search string")