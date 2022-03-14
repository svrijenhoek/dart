

class Document:

    # generic class that serves as superclass for the Article, User and Recommendation objects.
    # Not sure if this will be useful.

    def __init__(self, document):
        if 'id' in document:
            self.id = document['id']
        else:
            self.id = document['_id']
        # self.source = document['_source']
        if '_source' in document:
            self.source = document['_source']
        else:
            self.source = document
