from dart.handler.NLP.frog_handler import FrogHandler
from dart.handler.elastic.article_handler import ArticleHandler
from dart.models.Article import Article
import dart.Util
import time


article_handler = ArticleHandler()

project_name = dart.Util.random_string(8)
frog_handler = FrogHandler(project_name)

frog_handler.create_project()

articles = article_handler.search_with_query('Steur', 1000)

for x in articles:
    article = Article(x)
    print(article.title)
    frog_handler.add_document(article.text, article.title)

frog_handler.start_execution()

while not frog_handler.processing_finished():
    time.sleep(1)

files = frog_handler.get_filelist()
frog_handler.download_files(files)

frog_handler.delete_project()
