import re
from typing import List

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys

from scraping.article_scraper import ArticleScraper
from scraping.article import Article


class ResearchGate(ArticleScraper):

    @property
    def source_url(self) -> str:
        return "https://researchgate.net"

    def _get_search_page(self, query: str):
        self._driver.get("https://researchgate.net/")
        self._driver.wait_at_least_n_seconds_for(5, ".index-search-field__input")
        search_field = self._driver.find_element_by_css_selector(".index-search-field__input")
        search_field.click()
        search_field.clear()
        search_field.send_keys(query)
        search_field.send_keys(Keys.ENTER)
        self._driver.wait_at_least_n_seconds_for(5, 'div > a.nova-e-link[href^="publication"]')

    def _find_article_urls(self) -> List[str]:
        return [
            article_anchor.get_attribute("href")[:article_anchor.get_attribute("href").find("?")]
            for article_anchor in self._driver.find_elements_by_css_selector('div > a.nova-e-link[href^="publication"]')
        ]

    @property
    def _has_next_page(self):
        try:
            self._driver.find_element_by_css_selector("div:last-child  > a.nova-c-button")
            return True
        except NoSuchElementException:
            return False

    def _get_next_page(self):
        next_page_anchor = self._driver.find_element_by_css_selector("div:last-child  > a.nova-c-button")
        next_page_url = next_page_anchor.get_attribute("href")
        self._driver.get(next_page_url)
        self._driver.wait_at_least_n_seconds_for(5, 'div > a.nova-e-link[href^="publication"]')

    def _scrape_article_page(self, url: str) -> Article:
        self._driver.get_in_new_tab(url)
        self._driver.wait_at_least_n_seconds_for(5, ".research-detail-header-section")

        name = self._driver.find_element_by_css_selector("h1.research-detail-header-section__title").text

        author_anchor = self._driver.find_element_by_css_selector(
            ".js-authors-list .nova-v-person-list-item__align-content > div > a")
        author = author_anchor.text

        annotation = ""
        try:
            annotation = self._driver.find_element_by_css_selector('div[itemprop="description"]').text
        except NoSuchElementException:
            ...
        if annotation == "":
            try:
                pdf_text = self._driver.find_element_by_id("pdf-to-html-container").text
                abstract = pdf_text.find("ABSTRACT")
                keywords = pdf_text.find("KEY WORDS")
                if abstract != -1 and keywords != -1:
                    filtered_text = pdf_text[abstract + 10:keywords].replace('\n', ' ')
                    annotation = filtered_text
            except NoSuchElementException:
                ...
        if annotation == "":
            is_tab_open = False
            try:
                doi_anchor = self._driver.find_element_by_css_selector('a[href^="http://dx.doi.org"]')
                doi_url: str = doi_anchor.get_attribute('href')
                self._driver.get_in_new_tab(doi_url)
                is_tab_open = True
                try:
                    if "ieeexplore.ieee.org" in self._driver.current_url:
                        self._driver.wait_n_seconds_for(10, ".abstract-text")
                        annotation = self._driver.find_element_by_css_selector(".abstract-text").text[10:]
                    elif "springer.com" in self._driver.current_url:
                        self._driver.wait_n_seconds_for(10, "p.Para")
                        annotation = self._driver.find_element_by_css_selector("p.Para").text
                except TimeoutException:
                    ...
            except NoSuchElementException:
                ...
            finally:
                if is_tab_open:
                    self._driver.close_last_tab()
        if annotation == "":
            try:
                e = self._driver.find_element_by_css_selector(
                    ".research-detail-header-section__metadata  li:first-child")
                r = re.search("[1-3][0-9]{3}", e.text)
                if r is not None:
                    year_of_publication = int(e.text[r.start():r.end()])
                    if year_of_publication < 2000:
                        self._driver.close_last_tab()
                        return Article.create_empty(url)
            except NoSuchElementException:
                ...
        if annotation == "":
            self._logger.info(f"нельзя обработать {url}")

        document_url = "NA"
        try:
            anchor = self._driver.find_element_by_css_selector('a.nova-c-button[href^="https://www.researchgate"]')
            document_url = anchor.get_attribute("href")
        except NoSuchElementException:
            raise Exception(f'нет ссылки на скачивание "{name}"')

        self._driver.close_last_tab()
        return Article(name, author, annotation, self.source_url, url, document_url)
