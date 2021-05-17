import os
import sqlite3
from typing import List

from scraping.article import Article


class ArticleDB:
    __path = os.getcwd()

    def __init__(self) -> None:
        super().__init__()
        self._connection = sqlite3.connect(f"{ArticleDB.__path}/articles.db")
        cursor: sqlite3.Cursor = self._connection.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS articles"
            "(name TEXT,"
            " author TEXT,"
            " annotation TEXT,"
            " source_url TEXT,"
            " page_url TEXT,"
            " document_url TEXT)"
        )
        self._connection.commit()

    def __del__(self):
        self._connection.close()

    def is_page_scraped(self, url: str) -> bool:
        cursor: sqlite3.Cursor = self._connection.cursor()
        cursor.execute("SELECT page_url FROM articles WHERE page_url = ?", (url,))
        rows = cursor.fetchall()
        cursor.close()
        return len(rows) > 0

    def save_into_db(self, article: Article):
        cursor: sqlite3.Cursor = self._connection.cursor()
        cursor.execute("INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?)", article.as_tuple)
        cursor.close()
        self._connection.commit()

    @staticmethod
    def set_path(path: str):
        ArticleDB.__path = os.path.expanduser(path)

    @staticmethod
    def get_saved_articles() -> List[Article]:
        db_path = f"{ArticleDB.__path}/articles.db"
        try:
            connection = sqlite3.connect(db_path)
            cursor: sqlite3.Cursor = connection.cursor()
            cursor.execute("SELECT * from articles")
        except sqlite3.OperationalError:
            raise Exception(f"нет ДБ [{db_path}]")
        else:
            articles_as_tuples = cursor.fetchall()
        finally:
            cursor.close()
            connection.close()

        return [
            article
            for article in [Article(*a) for a in articles_as_tuples]
            if not article.is_empty
        ]
