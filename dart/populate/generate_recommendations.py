from datetime import datetime, timedelta

import numpy as np
import json

from dart.handler.elastic.connector import Connector
from dart.handler.elastic.article_handler import ArticleHandler
from dart.models.Article import Article


class RecommendationGenerator:

    """
    Class that generates baseline recommendations based on the articles stored in the 'articles' Elasticsearch index.
    Eight articles are 'recommended' following to the following three methods:
    - Random --> recommends randomly chosen articles
    - Most popular --> recommends the articles that have been shared most on Facebook
    - More like this --> recommends the articles that are most similar to what the user has read before

    """

    def __init__(self, documents, size):
        self.documents = documents
        self.size = size
        self.searcher = ArticleHandler()

    def generate_random(self):
        random_numbers = np.random.choice(len(self.documents), self.size, False)
        return [self.documents[i]['_id'] for i in random_numbers]

    def generate_most_popular(self):
        return [self.documents[i]['_id'] for i in range(int(self.size))]

    def generate_more_like_this(self, user, upper, lower):
        reading_history = user['_source']['reading_history']
        results = self.searcher.more_like_this_history(reading_history, upper, lower)
        return [results[i]['_id'] for i in range(min(int(self.size), len(results)))]


class RunRecommendations:

    def __init__(self, configuration):
        self.connector = Connector()
        self.searcher = ArticleHandler()

        self.timerange = configuration["recommendation_range"]
        self.size = configuration["recommendation_size"]
        self.dates = configuration["dates"]

        self.users = self.searcher.get_all_documents('users')

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
                "style": {
                    "complexity": article.get_style_metric('complexity'),
                    "nwords": article.get_style_metric('nwords'),
                    "nsentences": article.get_style_metric('nsentences')
                },
                "text": article.text,
                "title": article.title,
                "url": article.url
            }
        }
        return doc

    def add_to_index(self, json_doc):
        body = json.dumps(json_doc)
        self.connector.add_document('recommended_articles', doc_type='_doc', body=body)

    def add_document(self, date, user_id, rec_type, article):
        doc = self.create_json_doc(user_id, date, rec_type, article)
        self.add_to_index(doc)

    def execute(self):
        # go over every date specified in the config file
        for date in self.dates:
            print(date)
            # define the timerange for retrieving documents
            upper = datetime.strptime(date, '%d-%m-%Y')
            lower = upper - timedelta(days=self.timerange)
            # retrieve all the documents that are relevant for this date
            documents = self.searcher.get_all_in_timerange(lower, upper)
            # to account for a very sparse index
            recommendation_size = min(len(documents), self.size)

            rg = RecommendationGenerator(documents, recommendation_size)
            count = 0
            for user in self.users:
                try:
                    count = count+1
                    user_id = user['_id']
                    # generate random selection
                    random_recommendation = rg.generate_random()
                    for docid in random_recommendation:
                        article = Article(self.searcher.get_by_id('articles', docid))
                        self.add_document(date, user_id, 'random', article)
                    # select most popular
                    most_popular_recommendation = rg.generate_most_popular()
                    for docid in most_popular_recommendation:
                        article = Article(self.searcher.get_by_id('articles', docid))
                        self.add_document(date, user_id, 'most_popular', article)
                    # get more like the user has previously read
                    more_like_this_recommendation = rg.generate_more_like_this(user, upper, lower)
                    for docid in more_like_this_recommendation:
                        article = Article(self.searcher.get_by_id('articles', docid))
                        self.add_document(date, user_id, 'more_like_this', article)
                except KeyError:
                    print("Help, a Key Error occurred!")
                    continue
            print(count)


def execute(configuration):
    run = RunRecommendations(configuration)
    run.execute()

