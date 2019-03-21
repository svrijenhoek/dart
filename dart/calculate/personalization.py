from dart.handler.elastic.recommendation_handler import RecommendationHandler
from dart.handler.elastic.connector import Connector
from dart.models.Recommendation import Recommendation
import pandas as pd
import numpy as np
import difflib
import json
import sys


class Personalization:

    """
    Class to calculate the overall personalisation for each individual user
    Retrieves all recommendations made, and calculates the similarity between them per date
    """

    def __init__(self):
        self.searcher = RecommendationHandler()
        self.connector = Connector()

    # retrieves all recommendations found in the elasticsearch index
    def initialize(self):
        """
        Retrieves all recommendations in Elasticsearch
        Returns a Dataframe
        """
        recommendations = self.searcher.get_all_recommendations()
        table = []
        for entry in recommendations:
            recommendation = Recommendation(entry)
            table.append([recommendation.user, recommendation.date, recommendation.recommendations])
        columns = ['user_id', 'date', 'recommendations']
        return pd.DataFrame(table, columns=columns)

    def compare_recommendations(self, df):
        """
        :param df:
        :return:
        """
        dates = df.date.unique()
        # filter by date
        for date in dates:
            df1 = df[(df.date == date)]
            # for all users
            for _, x in df1.iterrows():
                recommendation_types = x.recommendations.keys()
                similarities = {}
                # compare to all other users
                for _, y in df.iterrows():
                    # do for each recommendation type
                    for key in recommendation_types:
                        rx = x.recommendations[key]
                        ry = y.recommendations[key]
                        similarity = self.calculate_similarity(rx, ry)
                        similarities[key].append(similarity)
                for key in similarities:
                    mean = self.calculate_mean(similarities[key])
                    self.add_document(x.user, key, mean)

    @staticmethod
    def calculate_similarity(x, y):
        """
        calculates for lists x and y how many elements they have in common
        output: 0..1, where 1 is a complete match and 0 is no match at all
        Input: two lists of docids
        Output: float

        >>> Personalization.calculate_similarity([0, 1, 2, 3], [0, 1, 2, 3])
        1.0
        >>> Personalization.calculate_similarity([0, 1, 2, 3], [2])
        0.4
        """
        sm = difflib.SequenceMatcher(None, x, y)
        return sm.ratio()

    @staticmethod
    def calculate_mean(a):
        """
        Calculate the mean value of a list
        Returns float
        >>> Personalization.calculate_mean([0.8, 0.2, 0.0])
        0.3333333333333333
        """
        return np.mean(a)

    def add_document(self, user, header, mean):
        """
        construct the json document that can be added to the elasticsearch index
        """
        doc = {
            'user': user,
            'type': header,
            'mean': mean,
        }
        body = json.dumps(doc)
        self.connector.add_document('personalization', '_doc', body)

    def execute(self):
        # retrieve all recommendations
        df = self.initialize()
        self.compare_recommendations(df)


def main(argv):
    run = Personalization()
    run.execute()


if __name__ == "__main__":
    main(sys.argv[1:])
