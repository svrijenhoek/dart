from dart.models.Recommendation import Recommendation
from dart.handler.elastic.base_handler import BaseHandler
import pandas as pd


class RecommendationHandler(BaseHandler):
    def __init__(self):
        super(RecommendationHandler, self).__init__()

    def get_all_recommendations(self):
        return super(RecommendationHandler, self).get_all_documents('recommendations')

    def get_recommendations_to_user(self, user_id):
        body = {
            "query": {
                "match": {
                    'recommendation.user_id': user_id
                }
            }
        }
        return super(RecommendationHandler, self).execute_search('recommendations', body)

    # common method for going through all articles in the articles index
    def get_recommendation_types(self):
        body = {
            "aggs": {
               "values": {
                 "cardinality": {
                   "field": 'recommendations.keyword'
                 }
                },
            }
        }
        output = super(RecommendationHandler, self).execute_search('recommendations', body)
        return [entry['_source']['recommendations'] for entry in output]

    # retrieves all recommendations found in the elasticsearch index
    def initialize(self):
        """
        Retrieves all recommendations in Elasticsearch
        Returns a Dataframe
        """
        recommendations = self.get_all_recommendations()
        table = []
        for entry in recommendations:
            recommendation = Recommendation(entry)
            table.append([recommendation.user, recommendation.date, recommendation.type, recommendation.article['id']])
        columns = ['user_id', 'date', 'recommendation_type', 'id']
        return pd.DataFrame(table, columns=columns)

