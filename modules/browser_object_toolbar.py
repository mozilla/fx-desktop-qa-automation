from modules.page_base import BasePage

class Toolbar(BasePage):

    URL_TEMPLATE = ""

    def wait_for_item_to_download(self, filename: str) -> BasePage:
        self.element_visible("downloads-item-by-file", labels=[filename])
        return self
