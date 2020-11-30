from dart.models.Document import Document


class Recommendation(Document):

    def __init__(self, document):
        Document.__init__(self, document)
        self.date = document['recommendation']['date']
        self.user = document['recommendation']['user_id']
        self.type = document['recommendation']['type']
        self.articles = document['articles']
