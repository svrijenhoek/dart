from dart.handler.elastic.base_handler import BaseHandler
import json


class OutputHandler(BaseHandler):

    def __init__(self, connector):
        self.connector = connector

    def add_aggregated_document(self, user_id, recommendation_type, style, personalization):
        """
        Adds the final result in the Elasticsearch database.
        TO DO: Mock ES and assert ES is called once
        """
        doc = {
            'user': user_id,
            'type': recommendation_type,
            'avg_popularity': style[0],
            'avg_complexity': style[1],
            'avg_nwords': style[2],
            'avg_nsentences': style[3],
            'personalization': personalization
        }
        body = json.dumps(doc)
        self.connector.add_document('aggregated_recommendations', '_doc', body)

    def add_location_document(self, date, recommendation_type, location):
        doc = {
            'date': date,
            'type': recommendation_type,
            'text': location[0],
            'country_code': location[1][0],
            'location': {
                'lat': location[1][1]['lat'],
                'lon': location[1][1]['lon']
            }
        }
        body = json.dumps(doc)
        self.connector.add_document('locations', '_doc', body)

    def add_occupation_document(self, doctype, user, date, doc_id, key, label, frequency):
        doc = {
            'type': doctype,
            'date': date,
            'user': user,
            'article_id': doc_id,
            key: {'name': label, 'frequency': frequency}
        }
        body = json.dumps(doc)
        self.connector.add_document('occupations', '_doc', body)

    def add_personalization_document(self, user, header, mean):
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
