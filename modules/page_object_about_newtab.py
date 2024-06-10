from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from modules.page_base import BasePage
import logging

class L10nAboutNewtab():
    def __init__(self, lang_code: str):
        # TODO: make l10ns for DE and FR
        if lang_code in ["enUS", "enUK", "deDE", "frFR"]:
            self.popular_topics = [
                "Self improvement",
                "Food",
                "Entertainment",
                "Health & fitness",
                "Science",
                "More recommendations ›"
            ]

class AboutNewtab(BasePage):
    URL_TEMPLATE = "about:newtab"

    def set_language_code(self, lang_code:str) -> BasePage:
        self.language = lang_code
        self.constants = L10nAboutNewtab(lang_code)
        return self

    def count_top_sites(self) -> int:
        top_sites_list = self.get_element("top-sites-list")
        top_site_nodes = top_sites_list.find_elements(By.TAG_NAME, "li")
        return len(top_site_nodes)

    def get_recommended_articles(self) -> list[WebElement]:
        article_root = self.get_element("recommended-by-pocket-list")
        return article_root.find_elements(By.TAG_NAME, "article")

    def count_recommended_articles(self) -> int:
        recd_articles = self.get_recommended_articles()
        return len(recd_articles)

    def check_article_alignment(self) -> bool:
        recd_articles = self.get_recommended_articles()
        number_of_articles = self.count_recommended_articles()
        for i in range(number_of_articles - 3, number_of_articles):
            article_x = recd_articles[i].location.get("x")
            for j in range(i-3, -1, -3):
                comparison_x = recd_articles[j].location.get("x")
                assert article_x == comparison_x
        return True

    def count_sponsored_articles(self) -> int:
        return len(
            self.get_elements("story-sponsored-footer")
        )

    def check_popular_topics(self) -> bool:
        poptopics_list = self.get_element("popular-topics-list")
        logging.info(f"Topics: {self.constants.popular_topics}")
        for li in poptopics_list.find_elements(By.TAG_NAME, "li"):
            logging.info(f"Topic innerText = {li.get_attribute('innerText')}")
            assert li.get_attribute("innerText") in self.constants.popular_topics
        return True

    def check_layout(self) -> BasePage:
        self.element_exists("incontent-search-input")
        logging.info("Search bar exists")
        self.element_exists("recent-activity-section")
        #self.element_visible("recent-activity-list")
        logging.info(f"found {self.count_top_sites()} top sites")
        # ODD: Sometimes we get 7 top sites, not 8
        assert self.count_top_sites() in [7,8]
        assert self.count_recommended_articles() == 21
        assert self.check_article_alignment()
        assert self.count_sponsored_articles() > 1
        assert self.check_popular_topics()

