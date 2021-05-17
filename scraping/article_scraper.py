import logging
from abc import ABC, abstractmethod
from typing import List, Iterator

from scraping.article import Article
from scraping.article_db import ArticleDB
from scraping.driver import Driver


class ArticleScraper(ABC):

    def __init__(self) -> None:
        super().__init__()
        self._driver = Driver()
        self._article_db = ArticleDB()
        self._logger = logging.getLogger(__name__)

    def __del__(self):
        self._driver.close()

    def scrape(self, queries: List[str]) -> Iterator[Article]:
        self._logger.info("started scraping")
        for query in queries:
            self._get_search_page(query)
            while True:
                yield from self.__scrape_search_page()
                if self._has_next_page:
                    self._logger.info("переход на следующую страницу результатов")
                    self._get_next_page()
                else:
                    break
        self._logger.info("done scraping")

    def __scrape_search_page(self) -> Iterator[Article]:
        urls = self._find_article_urls()
        for url in urls:
            if not self._article_db.is_page_scraped(url):
                article = self._scrape_article_page(url)
                self._article_db.save_into_db(article)
                self._logger.info(f"добавлено: {url} ")
                yield article
            else:
                self._logger.info(f"уже есть: {url} ")

    @property
    @abstractmethod
    def source_url(self) -> str:
        ...

    @abstractmethod
    def _get_search_page(self, query: str):
        ...

    @abstractmethod
    def _find_article_urls(self) -> List[str]:
        ...

    @abstractmethod
    def _get_next_page(self):
        ...

    @property
    @abstractmethod
    def _has_next_page(self) -> bool:
        ...

    @abstractmethod
    def _scrape_article_page(self, url: str) -> Article:
        ...
