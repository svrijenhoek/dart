from dart.handler.elastic.recommendation_handler import RecommendationHandler
from dart.handler.elastic.user_handler import UserHandler
from dart.handler.elastic.connector import Connector
from dart.models.Recommendation import Recommendation
from dart.models.User import User
import pandas as pd
import numpy as np
import difflib
import json


class Personalization:

    """
    Class to calculate the overall personalisation for each individual user
    Retrieves all recommendations made, and calculates the similarity between them per date
    """

    def __init__(self):
        self.searcher = RecommendationHandler()
        self.user_searcher = UserHandler()
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
            table.append([recommendation.user, recommendation.date, recommendation.type, recommendation.article['id']])
        columns = ['user_id', 'date', 'recommendation_type', 'id']
        return pd.DataFrame(table, columns=columns)

    def compare_recommendations(self, df):
        """
        Iterates over all recommendations, filters them down to the same date and recommendation type, and compares
        the similarities for all users. The result is put in the 'personalization' index in ES.
        """
        # filter by date
        for date in df.date.unique():
            # filter by recommendation type
            for rec_type in df.recommendation_type.unique():
                # get all users
                users = [User(entry) for entry in self.user_searcher.get_all_users()]
                dfx = df[(df.date == date) & (df.recommendation_type == rec_type)]
                # compare each user to all other users
                for user1 in users:
                    similarities = []
                    # filter dataframe for just the data of 1 date, recommendation type and user
                    df1 = dfx[dfx.user_id == user1.id]
                    articles1 = [row.id for _, row in df1.iterrows()]
                    for user2 in users:
                        df2 = dfx[dfx.user_id == user2.id]
                        articles2 = [row.id for _, row in df2.iterrows()]
                        similarity = self.calculate_similarity(articles1, articles2)
                        similarities.append(similarity)
                    mean = self.calculate_mean(similarities)
                    self.add_document(user1.id, rec_type, mean)

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

