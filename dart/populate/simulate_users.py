import json
import dart.Util as Util


class UserSimulator:

    def __init__(self, config, handlers):
        self.config = config
        self.handlers = handlers

    def simulate_similar_to_topic(self, n_topics, n_spread):
        reading_history = []
        # get articles around topics
        for _ in range(0, n_topics):
            spread = max(Util.get_random_number(n_spread, n_spread / 2), 5)
            document = self.handlers.articles.get_random_article()
            response = self.handlers.articles.get_similar_documents(document.id, spread)
            for article in response:
                reading_history.append(article.id)
        return reading_history

    def simulate_popular_stories(self, mean_popular):
        # add most popular stories
        reading_history = []
        n_popular = max(1, Util.get_random_number(mean_popular, mean_popular / 1.5))
        response = self.handlers.articles.get_most_popular(n_popular)
        for hit in response:
            reading_history.append(hit.id)
        return reading_history

    def simulate_random(self, mean_random):
        # add random articles
        reading_history = []
        n_random = Util.get_random_number(mean_random, mean_random / 1.5)
        for _ in range(0, n_random):
            article = self.handlers.articles.get_random_article()
            reading_history.append(article.id)
        return reading_history

    def execute(self):
        n_topics = self.config["user_topics"]
        n_spread = self.config["user_spread"]
        mean_popular = self.config["user_popular"]
        mean_random = self.config["user_random"]
        n_users = self.config["user_number"]

        for _ in range(0, n_users):
            # generate reading history
            similar_to_topic = self.simulate_similar_to_topic(n_topics, n_spread)
            popular_articles = self.simulate_popular_stories(mean_popular)
            random_articles = self.simulate_random(mean_random)
            reading_history = similar_to_topic + popular_articles + random_articles

            json_doc = {
                "reading_history": reading_history
            }

            body = json.dumps(json_doc)
            self.handlers.users.add_user(body)

