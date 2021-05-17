from typing import List

import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from scraping.article_scraper import ArticleScraper
from scraping.article import Article


class AcademicMicrosoft(ArticleScraper):

    @property
    def source_url(self) -> str:
        return "https://academic.microsoft.com"

    def select_checkbox(self, theme: str):
        self._driver.wait_at_least_n_seconds_for(8, '.filter-panel section:nth-child(2)')
        checkboxes = self._driver.find_elements_by_css_selector(".filter-panel section:nth-child(2) .data-bar-item")
        themes = [checkbox.text for checkbox in checkboxes]
        if theme in themes:
            checkbox = checkboxes[themes.index(theme)]
            checkbox.click()
            time.sleep(10)

    def _get_search_page(self, query: str):
        self._driver.get("https://academic.microsoft.com/")
        self._driver.wait_at_least_n_seconds_for(8, "#search-input")
        search_field = self._driver.find_element_by_css_selector("#search-input")
        search_field.click()
        search_field.clear()
        search_field.send_keys(query)
        search_field.send_keys(Keys.ENTER)

        # фильтр по нужным темам
        self.select_checkbox('Computer science')
        self.select_checkbox('Heuristic')
        self.select_checkbox('Mathematical optimization')

    def _find_article_urls(self) -> List[str]:
        return [
            article_anchor.get_attribute("href")
            for article_anchor in self._driver.find_elements_by_css_selector('a[href^=paper]')
        ]

    def _get_next_page(self):
        button = self._driver.find_element_by_css_selector('.icon-up.right')
        button.click()
        time.sleep(10)

    @property
    def _has_next_page(self) -> bool:
        try:
            self._driver.find_element_by_css_selector('.icon-up.right')
            return True
        except NoSuchElementException:
            return False

    def _scrape_article_page(self, url: str) -> Article:
        self._driver.get_in_new_tab(url)
        self._driver.wait_at_least_n_seconds_for(4, "h1.name")

        try:
            name = self._driver.find_element_by_css_selector("h1.name").text
            author_raw = self._driver.find_element_by_css_selector(".author-item:first-child").text
            author = "".join(c for c in author_raw if not c.isdigit() and not c == ",").strip()
            annotation = self._driver.find_element_by_css_selector("h3.caption + p").text
        except NoSuchElementException:
            self._logger.warning(f"нельзя обработать {url}")
            self._driver.close_last_tab()
            return Article.create_empty(url)
        else:
            self._driver.close_last_tab()
            return Article(name, author, annotation, self.source_url, url, "")
