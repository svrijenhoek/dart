from dart.models.Recommendation import Recommendation
from dart.handler.elastic.base_handler import BaseHandler
import pandas as pd


class RecommendationHandler(BaseHandler):
    def __init__(self):
        super(BaseHandler, self).__init__()

    @staticmethod
    def make_dataframe(docs):
        recommendations = [Recommendation(doc) for doc in docs]
        table = []
        for rec in recommendations:
            table.append(rec.date, rec.user, rec.recommendations)
        df = pd.DataFrame(table, columns=['date', 'user', 'recommendations'])
        return df

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

