from datetime import datetime, timedelta

import numpy as np
import json, sys

import Util
from Elastic.Connector import Connector
from Elastic.Search import Search


class RecommendationGenerator:

    def __init__(self, documents, size):
        self.documents = documents
        self.size = size
        self.searcher = Search()

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

    connector = Connector()
    searcher = Search()

    timerange = Util.read_config_file("recommendations", "range")
    size = Util.read_config_file("recommendations", "size")
    dates = Util.read_config_file("recommendations", "dates")

    users = searcher.get_all_documents('users')

    def execute(self):
        for date in self.dates:
            print(date)
            upper = datetime.strptime(date, '%d-%m-%Y')
            lower = upper - timedelta(days=self.timerange)
            documents = self.searcher.get_all_in_timerange('articles', 10000, lower, upper)
            recommendation_size = min(len(documents), self.size)

            rg = RecommendationGenerator(documents, recommendation_size)

            for user in self.users:
                user_id = user['_id']
                # generate random selection
                random_recommendation = rg.generate_random()
                # select most popular
                most_popular_recommendation = rg.generate_most_popular()
                # get more like the user has previously read
                more_like_this_recommendation = rg.generate_more_like_this(user, upper, lower)
                # add recommendations to elasticsearch
                json_doc = {
                    "user_id": user_id,
                    "date": date,
                    "recommendations": {
                        "random": random_recommendation,
                        "most_popular": most_popular_recommendation,
                        "more_like_this": more_like_this_recommendation
                    }
                }
                body = json.dumps(json_doc)
                docid = json_doc.pop('_id', None)
                self.connector.add_document('recommendations', docid, 'recommendation', body)


def main(argv):
    run = RunRecommendations()
    run.execute()


if __name__ == "__main__":
    main(sys.argv[1:])
