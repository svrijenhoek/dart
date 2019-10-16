from dart.models.Document import Document


class Recommendation(Document):

    def __init__(self, document):
        Document.__init__(self, document)
        self.date = self.source['recommendation']['date']
        self.user = self.source['recommendation']['user_id']
        self.type = self.source['recommendation']['type']
        self.articles = self.source['articles']
