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

    def add_to_queue(self, date, dates, identifier, docids, keywords, classification, title):
        doc = {
            'date': date,
            'dates': dates,
            'identifier': identifier,
            'title': title,
            'keywords': keywords,
            'classification': classification,
            'docids': docids
        }
        self.queue.append(doc)

    def get_stories_at_date(self, u, l):
        lower = l.strftime('%Y-%m-%dT%H:%M:%S')
        upper = u.strftime('%Y-%m-%dT%H:%M:%S')
        body = {
            'query': {"range": {
                "date": {
                    "lt": upper,
                    "gte": lower
                }
            }},
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
        if response:
            return Story(response[0])
        else:
            return None
