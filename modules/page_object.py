from dataclasses import dataclass
from selenium.webdriver.common.by import By


@dataclass
class AboutPrefs:
    # Docstring TK

    # Categories
    category_search = (By.ID, "category-search")

    # Category: Search elements
    search_engine_dropdown = (By.ID, "defaultEngine")
    search_engine_option = lambda engine_name: (
        By.CSS_SELECTOR,
        f"menuitem[label='{engine_name}']",
    )

    # Misc
    any_dropdown_active = (By.CSS_SELECTOR, "menuitem[_moz-menuactive='true']")


@dataclass
class AboutGlean:
    # Docstring TK

    # Elements
    ping_id_input = (By.ID, "tag-pings")
    submit_button = (By.ID, "controls-submit")
