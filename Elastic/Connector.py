from elasticsearch import Elasticsearch

# Class responsible for interacting with the Elasticsearch database. Supports CRUD operations. Might be split up if
# the need arises.


class Connector:

    es = Elasticsearch()

    def add_document(self, index, docid, type, body):
        self.es.index(index=index, doc_type=type, id=docid, body=body)

    def update_document(self, index, doctype, docid, body):
        self.es.update(index=index, doc_type=doctype, id=docid, body=body)

    def get_term_vector(self, index, doctype, docid):
        return self.es.termvectors(index=index, doc_type=doctype, id=docid, positions=True, term_statistics=True)


