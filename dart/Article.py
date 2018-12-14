from dart.Document import Document


class Article(Document):

    def __init__(self, document):
        Document.__init__(self, document)
        self.text = self.source['text']
        self.title = self.source['title']
        self.publication_date = self.source['publication_date']
        self.doctype = self.source['doctype']
        self.entities = self.source['entities']
        self.stylometrics = self.source['stylometrics']
        try:
            self.popularity = self.source['popularity']['facebook_share']
        except KeyError:
            self.popularity = 0

    def get_style_metric(self, metric):
        return self.stylometrics[metric]

    def get(self, x):
        return self.source[x]
