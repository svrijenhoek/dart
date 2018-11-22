import time
from Elastic.Connector import Connector

# Class dealing with all Elasticsearch Search operations. Contains the following queries:
# - most popular documents
# - random document
# - similar document
# - all documents in timerange


class Search(Connector):
    def __init__(self):
        super(Connector, self).__init__()

    def execute_search(self, index, body):
        response = self.es.search(index=index, body=body)
        return response['hits']['hits']

    def get_popularity_not_calculated(self):
        body = {
            "size": 10000,
            "query": {
                "bool": {
                    "must_not": {
                        "exists": {
                            "field": "popularity.facebook_share"
                            }
                    }
                }
            }
        }
        return self.execute_search('articles', body)

    def get_most_popular(self, size):
        body = {
            "size": size,
            "sort": [
                {"popularity.facebook_share": {"order": "desc", "mode": "max", "unmapped_type": "long"}}
            ],
            "query": {
                "match_all": {},
            }}
        return self.execute_search('articles', body)

    def get_random_document(self, index):
        timestamp = time.time()
        body = {
            "size": 1,
            "query": {
                  "function_score": {
                     "functions": [
                        {
                           "random_score": {
                              "seed": str(timestamp)
                           }
                        }
                     ]
                  }
            }}
        return self.execute_search(index, body)[0]

    def get_similar_documents(self, index, docid, size):
        body = {
            'size': size,
            'query': {"more_like_this": {
                "fields": ['text'],
                "like": [
                    {
                        "_index": index,
                        "_id": docid,
                    },
                ],
        }}}
        return self.execute_search(index, body)

    def get_all_in_timerange(self, index, size, lower, upper):
        size = 5000
        offset = 0
        all_documents = []

        body = {
            'size': size,
            'from': offset,
            "sort": [
                {"popularity.facebook_share": {"order": "desc", "mode": "max", "unmapped_type": "long"}}
            ],
            'query': {"range": {
                "publication_date": {
                    "lt": upper,
                    "gte": lower
                }
            }}}

        documents = self.execute_search(index, body)
        while len(documents) > 0:
            all_documents += documents
            offset += size
            body['from'] = offset
            documents = self.execute_search(index, body)

        return all_documents
        return self.execute_search(index, body)

    # Do not use this function for querying the articles index!
    def get_all_documents(self, index):
        size = 1000
        offset = 0
        all_documents = []

        body = {
            'size': size,
            'from': offset,
            "query": {
                "match_all": {}
            }
        }

        documents = self.execute_search(index, body)
        while len(documents) > 0:
            all_documents += documents
            offset += size
            body['from'] = offset
            documents = self.execute_search(index, body)

        return all_documents

    def get_by_id(self, index, id):
        body = {
            "query": {
                "terms": {
                    "_id": id
                }
            }
        }
        return self.execute_search(index, body)[0]

