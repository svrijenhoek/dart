from dart.models.Document import Document


class Article(Document):

    def __init__(self, document):
        Document.__init__(self, document)
        self.text = self.source['text']
        self.title = self.source['title']
        self.publication_date = self.source['publication_date']
        self.doctype = self.source['doctype']
        try:
            self.entities = self.source['entities']
        except KeyError:
            self.entities = ''
        try:
            self.tags = self.source['tags']
        except KeyError:
            self.tags = ''
        try:
            self.author = self.source['byline']
        except KeyError:
            self.author = ''
        try:
            self.complexity = self.source['complexity']
            self.nwords = self.source['nwords']
            self.nsentences = self.source['nsentences']
        except KeyError:
            self.complexity = ''
            self.nwords = ''
            self.nsentences = ''
        self.url = self.source['url']
        try:
            self.popularity = self.source['popularity']['facebook_share']
        except KeyError:
            self.popularity = 0
        try:
            self.recommended = self.source['recommended']
        except KeyError:
            self.recommended = []

    def get(self, x):
        return self.source[x]
