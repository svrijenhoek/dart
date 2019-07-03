import json
import os
import dart.Util as Util


class UserSimulator:

    def __init__(self, config, handlers):
        self.handlers = handlers

        self.n_topics = config["user_topics"]
        self.n_spread = config["user_spread"]
        self.mean_popular = config["user_popular"]
        self.mean_random = config["user_random"]
        self.n_users = config["user_number"]
        self.load_users = config["user_load"]
        if self.load_users == "Y":
            self.alternative_schema = config["user_alternative_schema"]
            self.folder = config["user_folder"]
            self.schema = Util.read_json_file(config['user_schema'])
            self.user_reading_history_based_on = config["user_reading_history_based_on"]

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

    def simulate_reading_history(self):
        # generate reading history
        similar_to_topic = self.simulate_similar_to_topic(self.n_topics, self.n_spread)
        popular_articles = self.simulate_popular_stories(self.mean_popular)
        random_articles = self.simulate_random(self.mean_random)
        reading_history = similar_to_topic + popular_articles + random_articles
        return reading_history

    def reading_history_to_ids(self, titles):
        ids = []
        for title in titles:
            article = self.handlers.articles.get_field_with_value('title', title)[0]
            ids.append(article.id)
        return ids

    def execute(self):
        if self.load_users == "Y":
            for path, _, files in os.walk(self.folder):
                for name in files:
                    # assumes all files are json-l, change this to something more robust!
                    for line in open((os.path.join(path, name))):
                        json_doc = json.loads(line)
                        if self.alternative_schema == "Y":
                            json_doc = Util.transform(json_doc, self.schema)
                            if 'reading_history' in json_doc:
                                if self.user_reading_history_based_on == "title":
                                    json_doc['reading_history'] = {'base': self.reading_history_to_ids(json_doc['reading_history'])}
                            else:
                                json_doc['reading_history'] = {'base': self.simulate_reading_history()}
                        body = json.dumps(json_doc)
                        self.handlers.users.add_user(body)
        # else:
        # simulate user data
        for _ in range(0, self.n_users):
            reading_history = self.simulate_reading_history()
            json_doc = {
                "reading_history": {'base': reading_history}
            }
            body = json.dumps(json_doc)
            self.handlers.users.add_user(body)

