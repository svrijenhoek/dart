from dart.Document import Document


class User(Document):

    def __init__(self):
        self.reading_history = self.source['reading_history']
