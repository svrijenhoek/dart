import dart.handler.elastic.article_handler
import dart.handler.elastic.recommendation_handler
import dart.handler.elastic.user_handler
import dart.handler.elastic.output_handler
import dart.handler.elastic.connector


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class Handlers:

    def __init__(self, elastic_connector):
        self.articles = dart.handler.elastic.article_handler.ArticleHandler(elastic_connector)
        self.users = dart.handler.elastic.user_handler.UserHandler(elastic_connector)
        self.recommendations = dart.handler.elastic.recommendation_handler.RecommendationHandler(elastic_connector)
        self.output = dart.handler.elastic.output_handler.OutputHandler(elastic_connector)
