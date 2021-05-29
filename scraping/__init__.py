from typing import List

from scraping.article import Article
from scraping.article_db import ArticleDB
from scraping.article_scraper import ArticleScraper
from scraping.articles_utils import generate_html, open_html
from scraping.scrapers.academicmicrosoft import AcademicMicrosoft
from scraping.scrapers.citeseerx import CiteSeerX
from scraping.scrapers.researchgate import ResearchGate


def scrape_every_source(queries: List[str]):
    for scraper in [ResearchGate, AcademicMicrosoft, CiteSeerX]:
        for _ in scraper().scrape(queries):
            ...


def set_db_path(path: str):
    ArticleDB.set_path(path)


def get_scraped_articles() -> List[Article]:
    return ArticleDB.get_saved_articles()
