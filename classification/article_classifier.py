import re

import numpy as np
import sklearn
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn import metrics
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from scraping import Article


class ArticleClassifier:
    """Классификатор статей, основанный на наивном байесовском алгоритме."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            min_df=5,
            max_df=0.9,
            preprocessor=ArticleClassifier._text_preprocessor,
            stop_words=stopwords.words('english')
        )
        self.classifier: sklearn.naive_bayes.MultinomialNB = None
        self.classes = []

    def train(self, train_set: sklearn.utils.Bunch):
        """
        Обучение классификатора

        :param train_set: набор, по которому классификатор обучается
        """
        x = self.vectorizer.fit_transform(train_set.data)
        y = train_set.target
        self.classifier = MultinomialNB(alpha=1).fit(x, y)
        self.classes = train_set.target_names

    def test(self, test_set: sklearn.utils.Bunch):
        """
        Оценка обученного классификатора

        :param test_set: набор, по которому классификатор оценивается
        """
        if self.classifier is None:
            raise Exception("Классификатор еще прошел обучение!")
        else:
            x = self.vectorizer.transform(test_set.data)
            predicted = self.classifier.predict(x)
            np.mean(predicted == test_set.target)
            print(metrics.classification_report(
                test_set.target,
                predicted,
                target_names=test_set.target_names
            ))

    def predict(self, article: Article) -> str:
        """
        Предсказывает, к какому классу относится заданная статья.

        :param article: статья, класс которой надо определить
        """
        if self.classifier is None:
            raise Exception("Классификатор еще не прошел обучение!")

        x = self.vectorizer.transform([f"{article.name}\n\n{article.annotation}"])
        predicted_index = self.classifier.predict(x)[0]
        predicted_class = self.classes[predicted_index]
        return predicted_class

    @staticmethod
    def _text_preprocessor(raw_text: bytes) -> str:
        """
        Препроцессор, через который проходят статьи.

        Текст преобразуется следующим образом:
            1. удаляются:
                1.1 все спец символы
                1.2 слова, состоящие из 1го символа
                1.3 лишние пробелы
            2. все символы преобразуются в нижний регистр
            3. каждое слово преобразуется в лексему
        """
        processed = re.sub(r'\W', ' ', str(raw_text))

        processed = re.sub(r'\s+[a-zA-Z]\s+', ' ', processed)
        processed = re.sub(r'\^[a-zA-Z]\s+', ' ', processed)

        processed = re.sub(r'\s+', ' ', processed, flags=re.I)
        processed = re.sub(r'^b\s+', '', processed)

        processed = processed.lower()
        processed = ' '.join(WordNetLemmatizer().lemmatize(word) for word in processed.split())

        return processed
