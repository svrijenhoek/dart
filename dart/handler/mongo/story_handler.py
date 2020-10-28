from dart.handler.mongo.base_handler import BaseHandler


class StoryHandler(BaseHandler):

    def __init__(self, connector):
        super(StoryHandler, self).__init__(connector)
        self.connector = connector
        self.queue = []

    def add_story(self, date, dates, identifier, docids, keywords, classification, title):
        doc = {
            'date': date,
            'dates': dates,
            'identifier': identifier,
            'title': title,
            'keywords': keywords,
            'classification': classification,
            'docids': docids
        }
        self.connector.insert_one('support', 'stories', doc)

    def get_story_with_id(self, docid):
        return super(StoryHandler, self).get_by_docid('other', 'stories', docid)

    def get_story_at_date(self, l, u):
        lower = l.strftime('%Y-%m-%dT%H:%M:%S')
        upper = u.strftime('%Y-%m-%dT%H:%M:%S')
        return self.connector.find('support', 'stories', {"date":{"$gte": lower, "$lt": upper}})
