from dart.handler.elastic.base_handler import BaseHandler
import json


class OutputHandler(BaseHandler):

    def __init__(self, connector):
        self.connector = connector

    def add_aggregated_document(self, user_id, range, date, recommendation_type, metrics):
        """
        Adds the final result in the Elasticsearch database.
        TO DO: Mock ES and assert ES is called once
        """
        doc = {
            'user': user_id,
            'range': range,
            'date': date,
            'type': recommendation_type,
            'avg_popularity': metrics[0],
            'avg_complexity': metrics[1],
            'avg_nwords': metrics[2],
            'avg_nsentences': metrics[3]
        }
        body = json.dumps(doc)
        self.connector.add_document('aggregated_recommendations', '_doc', body)

    def add_location_document(self, title, date, recommendation_type, location):
        doc = {
            'title': title,
            'date': date,
            'type': recommendation_type,
            'text': location[0],
            'country_code': location[1][0],
            'location': {
                'lat': location[1][1],
                'lon': location[1][2]
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
