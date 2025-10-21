import logging

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from modules.browser_object_navigation import Navigation
from modules.page_base import BasePage


class L10nAboutNewtab:
    """
    Class to set text constants for Newtab localization.
    """

    def __init__(self, lang_code: str):
        # TODO: make l10ns for DE and FR once we are testing these builds
        if lang_code in ["enUS", "enGB", "deDE", "frFR"]:
            self.popular_topics = [
                "Self improvement",
                "Food",
                "Entertainment",
                "Health & fitness",
                "Science",
                "More recommendations ›",
            ]


class AboutNewtab(BasePage):
    """
    Class that describes the POM of the about:newtab page.

    Attributes
    ----------
    driver: selenium.webdriver.Firefox
        WebDriver object under test

    lang_code: str
        The ISO-639-1 code of the language, followed by the ISO-3166-1 alpha-2 code
        of the region (country). examples: enUS, zhCN, jaJP, frFR

    constants: self.L10nAboutNewtab
        Instantiation of the constants object
    """

    URL_TEMPLATE = "about:newtab"
    TOP_SITES_TOTAL = [7, 8]
    REC_ARTICLE_TOTAL = 21

    def __init__(self, driver: Firefox, **kwargs):
        super().__init__(driver, **kwargs)
        self.navigation = Navigation(driver)

    def set_language_code(self, lang_code: str) -> BasePage:
        """
        Set the language code of the object, set self.constants as well
        """
        self.language = lang_code
        self.constants = L10nAboutNewtab(lang_code)
        return self

    def count_top_sites(self) -> int:
        """
        Find the top sites area and return the number of tiles in it
        """
        top_sites_list = self.get_element("top-sites-list")
        top_site_nodes = top_sites_list.find_elements(By.TAG_NAME, "li")
        return len(top_site_nodes)

    def get_recommended_articles(self) -> list[WebElement]:
        """
        Return a list of all recommended article nodes
        """
        article_root = self.get_element("recommended-by-pocket-list")
        return article_root.find_elements(By.TAG_NAME, "article")

    def check_article_alignment(self) -> bool:
        """
        Check that all article card elements are lined up with the elements in their columns
        """
        recd_articles = self.get_recommended_articles()
        number_of_articles = len(recd_articles)
        for i in range(number_of_articles - 3, number_of_articles):
            article_x = recd_articles[i].location.get("x")
            for j in range(i - 3, -1, -3):
                comparison_x = recd_articles[j].location.get("x")
                assert article_x == comparison_x
        return True

    def count_sponsored_articles(self) -> int:
        """
        Return the total number of sponsored article cards
        """
        return len(self.get_elements("story-sponsored-footer"))

    def check_popular_topics(self) -> bool:
        """
        Ensure that all the Popular Topics are as expected
        """
        poptopics_list = self.get_element("popular-topics-list")
        checked_topics = []
        logging.info(f"Topics: {self.constants.popular_topics}")
        for li in poptopics_list.find_elements(By.TAG_NAME, "li"):
            this_topic = li.get_attribute("innerText")
            logging.info(f"Topic innerText = {this_topic}")
            assert this_topic in self.constants.popular_topics
            checked_topics.append(this_topic)
        assert checked_topics == self.constants.popular_topics
        return True

    def check_layout(self) -> BasePage:
        """
        Main method to check about:newtab layout is as expected
        """
        self.element_exists("incontent-search-input")
        logging.info("Search bar exists")
        self.element_exists("recent-activity-section")

        for i in range(1, self.REC_ARTICLE_TOTAL + 1):
            document_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )
            target_y = int(document_height) // i
            # Sometimes we need to scroll around to force the article tile to load
            # We're waiting until the article tiles load to resolve flake
            for _ in range(2):
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                self.driver.execute_script("window.scrollTo(0, 0);")
                self.driver.execute_script(f"window.scrollTo(0, {target_y});")
            self.get_element("loaded-image-by-index", labels=[str(i)])

        assert len(self.get_recommended_articles()) == self.REC_ARTICLE_TOTAL
        assert self.check_article_alignment()
        assert self.count_sponsored_articles() > 0
        assert self.check_popular_topics()
        logging.info(f"Found {self.count_top_sites()} top sites")
        # ODD: Sometimes we get 7 top sites, not 8
        assert self.count_top_sites() in self.TOP_SITES_TOTAL

    @BasePage.context_content
    def get_topsite_element(self, tile_title: str):
        """Get a top site tile element by title."""
        return self.get_element("top-site-by-title", labels=[tile_title])

    @BasePage.context_content
    def open_topsite_context_menu_by_title(self, tile_title: str):
        """
        Opens the context menu for a top site tile by its title.
        Argument:
            tile_title: The title text of the tile (eg. "Wikipedia")
        """
        # Get the tile by title and right-click on it to open context menu
        tile = self.get_topsite_element(tile_title)
        self.context_click(tile)
        return self

    @BasePage.context_content
    def hover_topsite_and_verify_url(self, tile_title: str, expected_url: str):
        """
        Hovers over a top site tile and verifies the status panel shows the expected URL, displayed in the
        bottom-left corner of the new tab window.
        Arguments:
            tile_title: The title text of the tile (e.g., "Wikipedia")
            expected_url: The expected URL to be displayed in the status panel
        """
        tile = self.get_topsite_element(tile_title)
        self.hover(tile)
        navigation = Navigation(self.driver)
        actual_url = navigation.get_status_panel_url()
        assert expected_url in actual_url, (
            f"Expected '{expected_url}' in '{actual_url}'"
        )
        return self
