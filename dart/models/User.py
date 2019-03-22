from dart.models.Document import Document


class User(Document):

    def __init__(self, document):
        Document.__init__(self, document)
        self.reading_history = self.source['reading_history']
