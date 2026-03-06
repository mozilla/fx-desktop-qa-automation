import logging

from pypom import Region
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from modules.util import PomUtils


class Dropdown(Region):
    """
    PyPOM Region factory for Dropdown menus in about:prefs. See PyPOM docs on Regions.
    """

    def __init__(self, page, require_shadow=True, **kwargs):
        super().__init__(page, **kwargs)
        self.utils = PomUtils(self.page.driver)
        self.is_search_dropdown = (
            page.__class__.__name__ == "AboutPrefs"
            and page.url_kwargs.get("category") == "search"
        )
        if require_shadow:
            self.shadow_elements = self.utils.get_shadow_content(self.root)
            try:
                self.dropmarker = next(
                    el
                    for el in self.shadow_elements
                    if el.tag_name == "dropmarker"
                    or el.get_attribute("class") == "select-wrapper with-icon"
                )
            except StopIteration:
                logging.warning("Proceeding without dropmarker...")
                self.dropmarker = None

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

        if self.is_search_dropdown:
            # Wait for dropdown to be fully open and panel-list to exist, created dynamically.
            # get_shadow_content may return [shadow_root] (Selenium) or direct children (script);
            # panel-list is a child of the shadow root, so search inside when not found at top level.
            def wait_for_panel_list(_):
                self.shadow_elements = self.utils.get_shadow_content(self.root)
                for el in self.shadow_elements:
                    if el.tag_name == "panel-list":
                        return el
                    try:
                        panels = el.find_elements(By.TAG_NAME, "panel-list")
                        if panels:
                            return panels[0]
                    except Exception:
                        pass
                return None

            panel_element = self.wait.until(wait_for_panel_list)
            matching_menuitems = [
                el
                for el in panel_element.find_elements(By.TAG_NAME, "panel-item")
                if option_name in el.text
            ]
        else:
            matching_menuitems = [
                el
                for el in self.root.find_elements(By.CSS_SELECTOR, option_tag)
                if el.get_attribute(label_name) == option_name
            ]
        if len(matching_menuitems) == 0:
            return False
        elif len(matching_menuitems) == 1:
            if double_click:
                self.page.double_click(reference=matching_menuitems[0])
            else:
                matching_menuitems[0].click()
            if wait_for_selection:
                if self.is_search_dropdown:
                    if self.dropmarker is not None:
                        panel_trigger = self.dropmarker.find_element(
                            By.CLASS_NAME, "panel-trigger"
                        )
                    else:
                        # dropmarker can be None when get_shadow_content returns [shadow_root]
                        self.shadow_elements = self.utils.get_shadow_content(self.root)
                        panel_trigger = None
                        for el in self.shadow_elements:
                            try:
                                triggers = el.find_elements(By.CLASS_NAME, "panel-trigger")
                                if triggers:
                                    panel_trigger = triggers[0]
                                    break
                            except Exception:
                                pass
                        if panel_trigger is None:
                            raise ValueError(
                                "Could not find panel-trigger in search dropdown shadow DOM"
                            )
                    self.wait.until(lambda _: panel_trigger.text == option_name)
                else:
                    self.wait.until(EC.element_to_be_selected(matching_menuitems[0]))
            # self.root.send_keys(Keys.ESCAPE)
            return self
        else:
            raise ValueError("More than one menu item matched search string")
