import time
from dart.helper.elastic.connector import Connector

# Class dealing with all Elasticsearch Search operations. Contains the following queries:
# - most popular documents
# - random document
# - similar document
# - all documents in timerange


class QueryBuilder(Connector):
    def __init__(self):
        super(Connector, self).__init__()

    def execute_search(self, index, body):
        response = self.es.search(index=index, body=body)
        return response['hits']['hits']

    def execute_search_with_scroll(self, index, body):
        response = self.es.search(index=index, scroll='1m', body=body)
        return response['_scroll_id'], response['hits']['total']

    # returns the articles that have a certain field not populated. This is used for example when calculating the
    # popularity of articles.
    def get_not_calculated(self, field):
        body = {
            "size": 1000,
            "query": {
                "bool": {
                    "must_not": {
                        "exists": {
                            "field": field
                            }
                    }
                }
            }
        }
        return self.execute_search('articles', body)

    # gets all the documents for which a popularity score has been defined
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

    # returns all articles that have been shared on Facebook most often
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

    # gets a random document from a specified index
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

    # given a document id, retrieve the documents that are most similar to it according to Elastic's
    # More Like This functionality.
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

    # retrieve all documents published in a certain timerange (usually 3 days)
    def get_all_in_timerange(self, index, size, lower, upper):
        size = size
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
        while len(documents) > 0:
            all_documents += documents
            offset += size
            body['from'] = offset
            documents = self.execute_search(index, body)

        return all_documents

    # common method for going through all articles in the articles index
    def get_all_documents_with_offset(self, index, size):
        body = {
            'size': size,
            "query": {
                "match_all": {}
            }
        }
        return self.execute_search_with_scroll(index, body)

    # get elastic entry by id
    def get_by_id(self, index, docid):
        body = {
            "query": {
                "bool": {
                    "filter": {
                        "term": {
                            "_id": docid
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

    # common method for going through all articles in the articles index
    def get_unique_values(self, index, field):
        field_keyword = field+'.keyword'
        body = {
            "aggs": {
               "values": {
                 "cardinality": {
                   "field": field_keyword
                 }
                },
            }
        }
        output = self.execute_search(index, body)
        return [entry['_source'][field] for entry in output]

    def get_field_with_value(self, index, field, value):
        body = {
            "size": 10000,
             "query": {
                "match": {
                    field: value
                }
             }
        }
        return self.execute_search(index, body)

    # used in the 'more like this' recommendation generator. Finds more articles based on the users reading history
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

    def scroll(self, sid, scroll):
        return self.es.scroll(scroll_id=sid, scroll=scroll)
