from datetime import datetime, timedelta

import numpy as np
import json, sys

import dart.Util as Util
from dart.helper.elastic.connector import Connector
from dart.helper.elastic.querybuilder import QueryBuilder
from dart.models.Article import Article


class RecommendationGenerator:

    def __init__(self, documents, size):
        self.documents = documents
        self.size = size
        self.searcher = QueryBuilder()

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

    def __init__(self):
        self.connector = Connector()
        self.searcher = QueryBuilder()

        self.timerange = Util.read_config_file("recommendations", "range")
        self.size = Util.read_config_file("recommendations", "size")
        self.dates = Util.read_config_file("recommendations", "dates")

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
        docid = json_doc.pop('_id', None)
        self.connector.add_document('recommended_articles', docid, '_doc', body)

    def add_document(self, date, user_id, rec_type, article):
        doc = self.create_json_doc(user_id, date, rec_type, article)
        self.add_to_index(doc)

    def execute(self):
        # go over every date specified in the config file
        for date in self.dates:
            # define the timerange for retrieving documents
            upper = datetime.strptime(date, '%d-%m-%Y')
            lower = upper - timedelta(days=self.timerange)
            # retrieve all the documents that are relevant for this date
            documents = self.searcher.get_all_in_timerange('articles', 5000, lower, upper)
            # to account for a very sparse index
            recommendation_size = min(len(documents), self.size)

            rg = RecommendationGenerator(documents, recommendation_size)
            try:
                for user in self.users:
                    user_id = user['_id']
                    print(user_id)
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
                continue


def main(argv):
    run = RunRecommendations()
    run.execute()


if __name__ == "__main__":
    main(sys.argv[1:])
