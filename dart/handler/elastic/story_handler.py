from dart.handler.elastic.base_handler import BaseHandler
from dart.models.Story import Story
import json


class StoryHandler(BaseHandler):

    def __init__(self, connector):
        super(StoryHandler, self).__init__(connector)
        self.connector = connector
        self.queue = []

    def add_story(self, date, identifier, docids, keywords, classification, title):
        doc = {
            'date': date,
            'identifier': identifier,
            'title': title,
            'keywords': keywords,
            'classification': classification,
            'docids': docids
        }
        body = json.dumps(doc)
        self.connector.add_document('stories', '_doc', body)

    def add_bulk(self):
        self.connector.add_bulk('stories', '_doc', self.queue)
        self.queue = []

    def add_to_queue(self, date, identifier, docids, keywords, classification, title):
        doc = {
            'date': date,
            'identifier': identifier,
            'title': title,
            'keywords': keywords,
            'classification': classification,
            'docids': docids
        }
        self.queue.append(doc)

    def get_stories_at_date(self, date):
        body = {
            "size": 10000,
            "query": {
                "match": {
                    "date": {
                        "query": date,
                        "operator": "and"
                    }
                }
            }
        }
        response = self.connector.execute_search('stories', body)
        return [Story(i) for i in response]

    def get_story_with_id(self, docid):
        body = {
            "query": {
                "match": {
                    "docids": {
                        "query": docid,
                        "operator": "and"
                    }
                }
            }
        }
        response = self.connector.execute_search('stories', body)
        return Story(response[0])
