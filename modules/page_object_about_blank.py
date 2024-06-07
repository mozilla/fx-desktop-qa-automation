from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from modules.page_base import BasePage


class AboutBlank(BasePage):
    URL_TEMPLATE = "about:blank"

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

    def check_article_alignment(self):
        recd_articles = self.get_recommended_articles()
        for i in range(25, 28):
            for j in range(i, -1, -3):
                assert recd_articles[i].location.get("x") == recd_articles[
                    i
                ].location.get("x")

    def count_sponsored_articles(self) -> int:
        recd_articles = self.get_recommended_articles()
        sponsoreds = []
        for article in recd_articles:
            try:
                sponsor_label = article.find_element(
                    By.CLASS_NAME, "story-sponsored-label"
                )
                assert "Sponsored" in sponsor_label.text
                sponsoreds.append(article)
            except AssertionError:
                pass
        return len(sponsoreds)
