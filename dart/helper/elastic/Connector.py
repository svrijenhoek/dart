from elasticsearch import Elasticsearch

# Class responsible for interacting with the Elasticsearch database. Supports CRUD operations. Might be split up if
# the need arises.


class Connector:

    es = Elasticsearch()

    # add document to the specified elastic index
    def add_document(self, index, docid, doc_type, body):
        self.es.index(index=index, doc_type=doc_type, id=docid, body=body)

    # update a small part of the given document
    def update_document(self, index, doc_type, docid, body):
        self.es.update(index=index, doc_type=doc_type, id=docid, body=body)

    # retrieve the term vector for a given document
    def get_term_vector(self, index, doc_type, docid):
        return self.es.termvectors(index=index, doc_type=doc_type, id=docid, positions=True, term_statistics=True)

    def clear_index(self, index):
        self.es.indices.delete(index=index, ignore=[400, 404])

    def clear_all(self):
        self.clear_index('articles')
        self.clear_index('users')
        self.clear_index('recommendations')


