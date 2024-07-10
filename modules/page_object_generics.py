from modules.page_base import BasePage


class GenericPage(BasePage):
    """
    Generic POM for a page we don't care to map
    """

    URL_TEMPLATE = "{url}"


class GenericPdf(BasePage):
    """
    Generic POM for any page with an open PDF in it.
    """

    URL_TEMPLATE = "{pdf_url}"

    def get_green_highlighted_text(self) -> str:
        return self.get_element("highlighted-text").get_attribute("innerText")
