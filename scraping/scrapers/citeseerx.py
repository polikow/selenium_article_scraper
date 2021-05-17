from typing import List

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from scraping.article_scraper import ArticleScraper
from scraping.article import Article


class CiteSeerX(ArticleScraper):
    @property
    def source_url(self) -> str:
        return "https://citeseerx.ist.psu.edu"

    def _get_search_page(self, query: str):
        self._driver.get("https://citeseerx.ist.psu.edu/index")
        self._driver.wait_n_seconds_for(5, "input[name=q]")

        search_field = self._driver.find_element_by_css_selector("input[name=q]")
        search_field.click()
        search_field.clear()
        search_field.send_keys(query)
        search_field.send_keys(Keys.ENTER)

        self._driver.wait_n_seconds_for(5, ".result a.doc_details")

    @staticmethod
    def __filter_url(url: str) -> str:
        ampersand = url.find("&")
        if ampersand == -1:
            raise Exception("не могу найти &")
        return url[:ampersand]

    def _find_article_urls(self) -> List[str]:
        return [
            self.__filter_url(article_anchor.get_attribute("href"))
            for article_anchor in self._driver.find_elements_by_css_selector(".result a.doc_details")
        ]

    def _get_next_page(self):
        next_page_button = self._driver.find_element_by_css_selector("#pager > a")
        next_page_button.click()
        self._driver.wait_n_seconds_for(5, "#result_info")

    @property
    def _has_next_page(self) -> bool:
        try:
            self._driver.find_element_by_css_selector("#pager > a")
            return True
        except NoSuchElementException:
            return False

    def _scrape_article_page(self, url: str) -> Article:
        self._driver.get_in_new_tab(url)
        self._driver.wait_n_seconds_for(5, "h2")

        try:
            name = self._driver.find_element_by_css_selector("h2").text.strip()
            authors = self._driver.find_element_by_css_selector("#docAuthors").text.strip()
            authors_comma = authors.find(",")
            if authors_comma == -1:
                author = authors[3:].replace(".", " ").strip()
            else:
                author = authors[3:authors_comma].strip()
            annotation = self._driver.find_element_by_css_selector("#abstract p").text.strip()
            document_url = self._driver.find_element_by_css_selector('a[href^="/viewdoc/downlo"]').get_attribute('href')
        except NoSuchElementException:
            self._logger.warning(f"нельзя обработать {url}")
            self._driver.close_last_tab()
            return Article.create_empty(url)
        else:
            self._driver.close_last_tab()
            return Article(name, author, annotation, self.source_url, url, document_url)
