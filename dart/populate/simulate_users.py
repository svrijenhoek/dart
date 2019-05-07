import json
import dart.Util as Util
from dart.handler.elastic.connector import ElasticsearchConnector
from dart.handler.elastic.article_handler import ArticleHandler
from dart.handler.elastic.user_handler import UserHandler

connector = ElasticsearchConnector()
searcher = ArticleHandler(connector)
user_handler = UserHandler(connector)


def execute(configuration):
    n_users = configuration["user_number"]
    n_topics = configuration["user_topics"]
    n_spread = configuration["user_spread"]
    mean_popular = configuration["user_popular"]
    mean_random = configuration["user_random"]

    for _ in range(0, n_users):
        # generate reading history
        reading_history = []
        # get articles around topics
        for _ in range(0, n_topics):
            document = searcher.get_random_article()
            spread = max(Util.get_random_number(n_spread, n_spread/2), 5)
            response = searcher.get_similar_documents(document.id, spread)
            for article in response:
                reading_history.append(article.id)

        # add most popular stories
        n_popular = max(1, Util.get_random_number(mean_popular, mean_popular/1.5))
        response = searcher.get_most_popular(n_popular)
        for hit in response:
            reading_history.append(hit.id)

        # add random articles
        n_random = Util.get_random_number(mean_random, mean_random/1.5)
        for _ in range(0, n_random):
            article = searcher.get_random_article()
            reading_history.append(article.id)

        json_doc = {
            "spread": spread,
            "popular": n_popular,
            "random": n_random,
            "reading_history": reading_history
        }

        body = json.dumps(json_doc)
        connector.add_document('users', 'user', body)

