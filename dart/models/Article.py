from dart.models.Document import Document


class Article(Document):

    def __init__(self, document):
        Document.__init__(self, document)
        self.text = self.source['text']
        self.title = self.source['title']
        self.publication_date = self.source['publication_date']
        self.doctype = self.source['doctype']
        self.entities = self.source['entities']
        self.stylometrics = self.source['stylometrics']
        self.complexity = self.stylometrics['complexity']
        self.nwords = self.stylometrics['nwords']
        self.nsentences = self.stylometrics['nsentences']
        self.url = self.source['url']
        try:
            self.popularity = self.source['popularity']['facebook_share']
        except KeyError:
            self.popularity = 0
        try:
            self.recommended = self.source['recommended']
        except KeyError:
            self.recommended = []

    def get_style_metric(self, metric):
        return self.stylometrics[metric]

    def get(self, x):
        return self.source[x]
