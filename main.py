import classification
import scraping

# # 1) скрейпинг
scraping.set_db_path("data")
scraping.scrape_every_source(["3d bin packing",
                              "3d bin packing problem",
                              "three-dimensional bin packing"])

# # 2) создание набора вручную классифицированных статей
scraping.set_db_path("data")
all_articles = scraping.get_scraped_articles()
classification.create_classified_set(all_articles, ["relevant", "irrelevant"], "data/set")

# 3) фильтрация статей
scraping.set_db_path("data")
all_articles = scraping.get_scraped_articles()
train_set = classification.load_set("data/train_set")
test_set = classification.load_set("data/test_set")
classifier = classification.ArticleClassifier()
classifier.train(train_set)
classifier.test(test_set)

filtered_articles = [a for a in all_articles if classifier.predict(a) == "relevant"]
filtered_downloadable_articles = [a for a in all_articles if a.has_download_link]

# 4) генерация html страниц:
scraping.generate_html("data/articles_all.html", "Все", all_articles)
scraping.generate_html("data/articles_relevant.html", "Полезные", filtered_articles)
scraping.generate_html("data/articles_relevant_downloadable.html", "Полезные", filtered_downloadable_articles)
