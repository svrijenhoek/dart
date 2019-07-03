from dart.models.Recommendation import Recommendation
from dart.handler.elastic.base_handler import BaseHandler
import pandas as pd


class RecommendationHandler(BaseHandler):
    def __init__(self, connector):
        super(RecommendationHandler, self).__init__(connector)
        self.connector = connector
        self.all_recommendations = None

    def add_recommendation(self, doc):
        self.connector.add_document('recommendations', '_doc', doc)

    def add_bulk(self, docs):
        self.connector.add_bulk('recommendations', '_doc', docs)

    def get_all_recommendations(self):
        if self.all_recommendations is None:
            recommendations = super(RecommendationHandler, self).get_all_documents('recommendations')
            self.all_recommendations = [Recommendation(i) for i in recommendations]
        return self.all_recommendations

    def update_doc(self, article_id, doc):
        recommendations = self.find_recommendations_with_article(article_id)
        for recommendation in recommendations:
            body = {
                "doc": doc
            }
            self.connector.update_document('recommendations', '_doc', recommendation.id, body)

    def get_recommendations_to_user(self, user_id, recommendation_type):
        body = {
            "size": 10000,
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "recommendation.user_id": user_id
                            }
                        },
                        {
                            "match": {
                                "recommendation.type": recommendation_type
                            }
                        }
                    ]
                }
            }
        }
        response = self.connector.execute_search('recommendations', body)
        return [Recommendation(i) for i in response]

    # common method for going through all articles in the articles index
    def get_recommendation_types(self):
        body = {
              "query": {
                "match_all": {}
              },
              "aggregations": {
                "label_agg": {
                  "terms": {
                    "field": "recommendation.type",
                    "size": 100
                  }
                }
              }
            }
        response = self.connector.execute_search('recommendations', body)
        output = [entry['_source']['recommendation']['type'] for entry in response]
        output_set = set(output)
        return list(output_set)

    def find_recommendations_with_article(self, article_id):
        body = {
            "size": 10000,
            "query": {
                "match": {
                    'article.id': article_id
                }
             }
        }
        response = self.connector.execute_search('recommendations', body)
        return [Recommendation(i) for i in response]

    # retrieves all recommendations found in the elasticsearch index
    def initialize(self):
        """
        Retrieves all recommendations in Elasticsearch
        Returns a Dataframe
        """
        recommendations = self.get_all_recommendations()
        table = []
        for recommendation in recommendations:
            table.append([recommendation.user, recommendation.date, recommendation.type, recommendation.article['id']])
        columns = ['user_id', 'date', 'recommendation_type', 'id']
        return pd.DataFrame(table, columns=columns)

