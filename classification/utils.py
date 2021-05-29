import os
import random
import shutil
from typing import List

import nltk
import sklearn.utils
from sklearn.datasets import load_files

import scraping

nltk.download('stopwords')


def underlined_prefix(text: str, n: int) -> str:
    """
    :param text: текст, начало которого надо подчеркнуть
    :param n: количество первых символов, которые надо подчеркнуть
    :return: текст с подчеркнутыми первыми символами.
    """
    return f"\033[4m{text[:n]}\033[0m{text[n:]}"


def create_classified_set(articles: List[scraping.Article],
                          classes: List[str],
                          path: str):
    """
    Утилита для ручной классификации статей.

    :param articles: статьи, которые можно классифицировать
    :param classes: классы, по которым классифицируются статьи
    :param path: директория, в которую сохраняется классифицированный набор
    """
    assert len(articles) > 0
    assert len(classes) > 1

    if os.path.exists(f"{path}"):
        shutil.rmtree(f"{path}")

    if not os.path.exists(path):
        os.mkdir(path)

    for class_ in classes:
        os.mkdir(f"{path}/{class_}")

    prefix_size = 1
    prefixes = [c[:prefix_size] for c in classes]
    while len(set(prefixes)) != len(classes):
        prefix_size += 1
        prefixes = [c[:prefix_size] for c in classes]

    classes_with_underlined_first_letters = \
        ' | '.join([underlined_prefix(c, prefix_size) for c in classes])
    helper = f"[{classes_with_underlined_first_letters}]"

    pairs = {c[:prefix_size]: c for c in classes}
    articles_per_class = {c: 0 for c in classes}

    try:
        for article in random.sample(articles, len(articles)):
            selected_class_prefix = input(
                f"{article}\n\n"
                f"{'; '.join(f'{class_}: {articles_per_class[class_]}' for class_ in classes)}\n"
                f"Введи подчеркнутые буквы нужно класса; Ничего для пропуска; Ctrl+c для остановки)\n"
                f"Класс этой статьи: {helper}"
            )
            selected_class = pairs.get(selected_class_prefix)
            if selected_class is None:
                continue

            article.save_into_directory(f"{path}/{selected_class}")
            articles_per_class[selected_class] += 1
    except KeyboardInterrupt:
        ...


def load_set(path: str) -> sklearn.utils.Bunch:
    """Загружает из заданной директории классифицированный набор"""
    return load_files(path)
