from dart.models.Recommendation import Recommendation
from dart.handler.elastic.base_handler import BaseHandler
import pandas as pd


class RecommendationHandler(BaseHandler):
    def __init__(self, connector):
        super(RecommendationHandler, self).__init__(connector)
        self.connector = connector
        self.all_recommendations = None
        self.queue = []

    def add_recommendation(self, doc):
        self.connector.add_document('recommendations', '_doc', doc)

    def add_bulk(self):
        self.connector.add_bulk('recommendations', '_doc', self.queue)
        self.queue = []

    def get_all_recommendations(self):
        if self.all_recommendations is None:
            recommendations = super(RecommendationHandler, self).get_all_documents('recommendations')
            self.all_recommendations = [Recommendation(i) for i in recommendations]
        return self.all_recommendations

    def get_recommendations_at_date(self, date, recommendation_type):
        body = {
            "size": 500,
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "recommendation.date": {
                                    "query": date,
                                    "operator": "and"
                                }
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
              "aggs": {
                "recommendation_types": {
                    "terms": {"field": "recommendation.type"}
                }
              }
            }
        response = self.connector.execute_aggregation('recommendations', body, 'recommendation_types')
        output = [entry['key'] for entry in response['buckets']]
        return output

    def find_recommendations_with_article(self, article_id):
        body = {
            "size": 10000,
            "query": {
                "match": {
                    'articles': article_id
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
            for article_id in recommendation.articles:
                table.append([recommendation.user, recommendation.date, recommendation.type, article_id])
        columns = ['user_id', 'date', 'recommendation_type', 'id']
        return pd.DataFrame(table, columns=columns)

    @staticmethod
    def create_json_doc(user_id, date, recommendation_type, articles):
        doc = {
            "recommendation": {
                "user_id": user_id,
                "date": date,
                "type": recommendation_type
            },
            "articles": articles
        }
        return doc

    def add_to_queue(self, date, user_id, rec_type, article):
        doc = self.create_json_doc(user_id, date, rec_type, article)
        self.queue.append(doc)

