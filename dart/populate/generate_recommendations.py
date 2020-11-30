from datetime import datetime, timedelta
import os
import json
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
        results = self.handlers.articles.more_like_this_history(user, upper, lower)
        return [results[i].id for i in range(min(int(self.size), len(results)))]

    def generate_political(self, user, upper, lower):
        political_documents = self.handlers.articles.get_political(user, upper, lower)
        return [political_documents[i].id for i in range(min(len(political_documents), self.size))]


class RunRecommendations:

    def __init__(self, config, handlers):
        self.handlers = handlers
        self.timerange = config["recommendation_range"]
        self.size = config["recommendation_size"]
        self.dates = config["recommendation_dates"]

        self.users = self.handlers.users.get_all_users()
        self.baseline_recommendations = config['baseline_recommendations']
        self.exhaustive = config["exhaustive"]
        self.load_recommendations = config['recommendations_load']
        if self.load_recommendations == 'Y':
            self.folder = config['recommendations_folder']

    def generate_recommendations(self, user, date, upper, lower, generator):
        # generate random selection
        if 'random' in self.baseline_recommendations:
            random_recommendation = generator.generate_random()
            self.handlers.recommendations.add_to_queue(date, user.id, 'random', random_recommendation)
        # select most popular
        if 'most_popular' in self.baseline_recommendations:
            most_popular_recommendation = generator.generate_most_popular()
            self.handlers.recommendations.add_to_queue(date, user.id, 'most_popular', most_popular_recommendation)
        # get more like the user has previously read
        if 'more_like_this' in self.baseline_recommendations:
            more_like_this_recommendation = generator.generate_more_like_this(user, upper, lower)
            self.handlers.recommendations.add_to_queue(date, user.id, 'more_like_this', more_like_this_recommendation)
        # get more like the user has previously read
        if 'political' in self.baseline_recommendations:
            political_recommendation = generator.generate_political(user, upper, lower)
            self.handlers.recommendations.add_to_queue(date, user.id, 'political', political_recommendation)
        self.handlers.recommendations.add_bulk()

    def load(self):
        for path, _, files in os.walk(self.folder):
            for name in files:
                # assumes all files are json-l, change this to something more robust!
                for line in open((os.path.join(path, name))):
                    json_doc = json.loads(line)
                    # if self.schema:
                    #     json_doc = Util.transform(json_doc, self.schema)
                    if json_doc:
                        date = json_doc['date']
                        date = datetime.strptime(date, '%d-%M-%Y').strftime('%Y-%M-%d')
                        user_id = json_doc['user_id']
                        recommendation_type = json_doc['type']
                        # to account for nan article ids
                        articles = [article_id for article_id in json_doc['articles'] if not article_id != article_id]
                        self.handlers.recommendations.add_to_queue(date, user_id, recommendation_type, articles)

                    if len(self.handlers.recommendations.queue) > 1000:
                        self.handlers.recommendations.add_bulk()

        if self.handlers.recommendations.queue:
            self.handlers.recommendations.add_bulk()

    def generate_reading_histories(self):
        for recommendation_type in self.handlers.recommendations.get_recommendation_types():
            for user in self.users:
                recommendations = self.handlers.recommendations.get_recommendations_to_user(user.id, recommendation_type)
                user.reading_history[recommendation_type] = {str(entry.date): entry.articles for entry in recommendations}
                self.handlers.users.update_user(user)

    def execute(self):
        if self.load_recommendations == 'Y':
            self.load()
        # go over every date specified in the config file
        if self.baseline_recommendations:
            for date in self.dates:
                # define the timerange for retrieving documents
                upper = datetime.strptime(date, '%Y-%m-%d')
                lower = upper - timedelta(days=self.timerange)
                # retrieve all the documents that are relevant for this date
                documents = self.handlers.articles.get_all_in_timerange(lower, upper)
                # retrieve all recommendations at date if exhaustive = minimal. This causes an exception when no own
                # recommendations are loaded.
                if self.exhaustive == 'minimal':
                    rec_at_date = self.handlers.recommendations.get_users_with_recommendations_at_date(date, 'custom')
                # to account for a very sparse index
                recommendation_size = min(len(documents), self.size)
                rg = RecommendationGenerator(documents, recommendation_size, self.handlers)
                if self.exhaustive == 'full':
                    user_base = self.users
                elif self.exhaustive == 'minimal':
                    user_base = [self.handlers.users.get_by_id(i) for i in rec_at_date]
                for user in user_base:
                    try:
                        self.generate_recommendations(user, date, upper, lower, rg)
                    except KeyError:
                        print("Help, a Key Error occurred!")
                        continue
        # self.generate_reading_histories()

