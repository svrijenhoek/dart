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

    def execute_query(self, index, query):
        body = query
        return self.execute_search(index, body)

    def get_document_by_text(self, text):
        body = {
            "query": {
                "constant_score": {
                    "filter": {
                        "term": {
                            "text": text
                        }
                    }
                }
            }
        }
        return self.execute_search('articles', body)

    def get_not_calculated(self, type):
        body = {
            "size": 1000,
            "query": {
                "bool": {
                    "must_not": {
                        "exists": {
                            "field": type
                            }
                    }
                }
            }
        }
        return self.execute_search('articles', body)

    def get_popularity_calculated_with_offset(self, offset):
        body = {
            "size": 1000,
            "from": offset,
            "query": {
                "bool": {
                    "must": {
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
        while len(documents) > 0 and offset < 2000:
            all_documents += documents
            offset += size
            body['from'] = offset
            documents = self.execute_search(index, body)

        return all_documents

    def get_all_documents_with_offset(self, index, size, offset):
        body = {
            'size': size,
            'from': offset,
            "query": {
                "match_all": {}
            }
        }

        return self.execute_search(index, body)

    def get_by_id(self, index, id):
        body = {
            "query": {
                "bool": {
                    "filter": {
                        "term": {
                            "_id": id
                        }
                    }
                }
            }
        }
        return self.execute_search(index, body)[0]

    def get_by_url(self, index, url):
        body = {
            "query": {
                "match": {
                    "url": url
                }
            }
        }
        output = self.execute_search(index, body)
        return output[0]

    def more_like_this_history(self, reading_history, upper, lower):
        like_query = [{"_index": "articles", "_id": doc} for doc in reading_history]
        body = {
            'query': {
                "bool": {
                    "must": {
                        "range": {
                            "publication_date": {
                                "lt": upper,
                                "gte": lower
                            }
                        },
                    },
                    "should": {
                        "more_like_this": {
                            "fields": ['text'],
                            "like": like_query
                        }
                    }
                }
            }
        }
        return self.execute_search('articles', body)
