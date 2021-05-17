import os
import textwrap

from pydantic.dataclasses import dataclass


def wrap(text: str) -> str:
    return '\n'.join(textwrap.wrap(text, 80))


class ArticleSavedAlreadyException(Exception):
    pass


@dataclass
class Article:
    name: str
    author: str
    annotation: str
    source_url: str
    page_url: str
    document_url: str

    @staticmethod
    def create_empty(page_url: str):
        return Article("", "", "", "", page_url, "")

    @property
    def is_empty(self) -> bool:
        return self.name == "" and \
               self.author == "" and \
               self.annotation == "" and \
               self.source_url == "" and \
               self.document_url == ""

    @property
    def has_download_link(self) -> bool:
        return not (
                self.annotation == "" or
                self.author == "" or
                self.document_url == "" or
                len(self.annotation) < 100 or
                (self.source_url == "https://researchgate.net" and "citation" in self.document_url)
        )

    @property
    def as_tuple(self) -> tuple:
        return (self.name,
                self.author,
                self.annotation,
                self.source_url,
                self.page_url,
                self.document_url)

    @property
    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "author": self.author,
            "annotation": self.annotation,
            "source_url": self.source_url,
            "page_url": self.page_url,
            "document_url": self.document_url
        }

    def save_into_directory(self, directory_path: str):
        file_path = self.__save_path(directory_path)
        if os.path.exists(file_path):
            raise ArticleSavedAlreadyException()
        with open(file_path, "w") as file:
            file.write(f"{self.name}\n\n{self.annotation}")

    @property
    def short_source_url(self) -> str:
        without_protocol = self.source_url.replace("https://", '').replace("http://", '')
        last_dot = without_protocol.rfind('.')
        if last_dot == -1:
            raise Exception("нельзя выделить короткое название сайта")
        else:
            return without_protocol[:last_dot].replace('.', '_')

    @property
    def name_without_special_chars(self) -> str:
        return self.name.replace(',', '_').replace('.', '_').replace(' ', '_').replace('/', '_')

    def __save_path(self, directory_path: str) -> str:
        return f"{directory_path}/{self.short_source_url}__{self.name_without_special_chars}.txt"

    def __str__(self):
        return f'\033[1m{wrap(self.name)}\033[0m\n\n' \
               f'{wrap(self.annotation)}\n\n{self.page_url}'
