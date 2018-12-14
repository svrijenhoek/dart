from dart.Document import Document


class Recommendation(Document):

    def __init__(self, document):
        Document.__init__(self, document)
        self.date = self.source['date']
        self.user = self.source['user_id']
        self.recommendations = self.source['recommendations']

    def get_recommendation_types(self):
        return self.recommendations.keys()

    def get_articles_for_type(self, type):
        return self.recommendations[type]
