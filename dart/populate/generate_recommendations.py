from datetime import datetime, timedelta
import numpy as np


class RecommendationGenerator:

    """
    Class that generates baseline recommendations based on the articles stored in the 'articles' Elasticsearch index.
    Eight articles are 'recommended' following to the following three methods:
    - Random --> recommends randomly chosen articles
    - Most popular --> recommends the articles that have been shared most on Facebook
    - More like this --> recommends the articles that are most similar to what the user has read before

    """

    def __init__(self, documents, size, handlers):
        self.documents = documents
        self.size = size
        self.handlers = handlers

    def generate_random(self):
        random_numbers = np.random.choice(len(self.documents), self.size, False)
        return [self.documents[i].id for i in random_numbers]

    def generate_most_popular(self):
        return [self.documents[i].id for i in range(int(self.size))]

    def generate_more_like_this(self, user, upper, lower):
        reading_history = user.reading_history
        results = self.handlers.articles.more_like_this_history(reading_history, upper, lower)
        return [results[i].id for i in range(min(int(self.size), len(results)))]


class RunRecommendations:

    def __init__(self, config, handlers):
        self.handlers = handlers
        self.timerange = config["recommendation_range"]
        self.size = config["recommendation_size"]
        self.dates = config["recommendation_dates"]

        self.users = self.handlers.users.get_all_users()

        self.queue = []

    @staticmethod
    def create_json_doc(user_id, date, recommendation_type, article):
        doc = {
            "recommendation": {
                "user_id": user_id,
                "date": date,
                "type": recommendation_type
            },
            "article": {
                "id": article.id,
                "source": article.doctype,
                "popularity": article.popularity,
                "publication_date": article.publication_date,
                "text": article.text,
                "title": article.title,
                "url": article.url
            }
        }
        return doc

    def add_document(self, date, user_id, rec_type, article):
        doc = self.create_json_doc(user_id, date, rec_type, article)
        self.queue.append(doc)
        if len(self.queue) % 100 == 0:
            self.handlers.recommendations.add_bulk(self.queue)

    def generate_recommendations(self, user, date, upper, lower, generator):
        # generate random selection
        random_recommendation = generator.generate_random()
        for docid in random_recommendation:
            article = self.handlers.articles.get_by_id(docid)
            self.add_document(date, user.id, 'random', article)
        # select most popular
        most_popular_recommendation = generator.generate_most_popular()
        for docid in most_popular_recommendation:
            article = self.handlers.articles.get_by_id(docid)
            self.add_document(date, user.id, 'most_popular', article)
        # get more like the user has previously read
        more_like_this_recommendation = generator.generate_more_like_this(user, upper, lower)
        for docid in more_like_this_recommendation:
            article = self.handlers.articles.get_by_id(docid)
            self.add_document(date, user.id, 'more_like_this', article)

    def execute(self):
        # go over every date specified in the config file
        for date in self.dates:
            # define the timerange for retrieving documents
            upper = datetime.strptime(date, '%d-%m-%Y')
            lower = upper - timedelta(days=self.timerange)
            # retrieve all the documents that are relevant for this date
            documents = self.handlers.articles.get_all_in_timerange(lower, upper)
            # to account for a very sparse index
            recommendation_size = min(len(documents), self.size)
            rg = RecommendationGenerator(documents, recommendation_size, self.handlers)
            count = 0
            for user in self.users:
                try:
                    count = count + 1
                    self.generate_recommendations(user, date, upper, lower, rg)
                except KeyError:
                    print("Help, a Key Error occurred!")
                    continue
        if len(self.queue) > 0:
            self.handlers.recommendations.add_bulk(self.queue)

