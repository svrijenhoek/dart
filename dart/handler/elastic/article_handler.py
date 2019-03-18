from datetime import datetime
from dart.handler.elastic.base_handler import BaseHandler

# Class dealing with all Elasticsearch Search operations. Contains the following queries:
# - most popular documents
# - random document
# - similar document
# - all documents in timerange


class ArticleHandler(BaseHandler):
    def __init__(self):
        super(ArticleHandler, self).__init__()

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
        return super(ArticleHandler, self).execute_search('articles', body)

    # search with query
    def search_with_query(self, query, size):
        body = {
            "size": size,
            "query": {
                "match": {
                    "text": query
                }
            }
        }
        return super(ArticleHandler, self).execute_search('articles', body)

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
        return super(ArticleHandler, self).execute_search('articles', body)

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
        return super(ArticleHandler, self).execute_search('articles', body)

    # gets a random document from a specified index
    def get_random_article(self):
        return super(ArticleHandler, self).get_random('articles')

    # given a document id, retrieve the documents that are most similar to it according to Elastic's
    # More Like This functionality.
    def get_similar_documents(self, docid, size):
        body = {
            'size': size,
            'query': {"more_like_this": {
                "fields": ['text'],
                "like": [
                    {
                        "_index": 'articles',
                        "_id": docid,
                    },
                ],
        }}}
        return super(ArticleHandler, self).execute_search('articles', body)

    def get_all_in_timerange(self, l, u):
        lower = datetime.strptime(l, '%d-%m-%Y')
        upper = datetime.strptime(u, '%d-%m-%Y')
        docs = []
        body = {
            'query': {"range": {
                "publication_date": {
                    "lt": upper,
                    "gte": lower
                }
            }
            }
        }
        sid, scroll_size = super(ArticleHandler, self).execute_search_with_scroll('articles', body)
        # Start retrieving documents
        while scroll_size > 0:
            result = super(ArticleHandler, self).scroll(sid, '2m')
            sid = result['_scroll_id']
            scroll_size = len(result['hits']['hits'])
            for hit in result['hits']['hits']:
                docs.append(hit)
        return docs

    # get elastic entry by id
    def get_by_docid(self, docid):
        return super(ArticleHandler, self).get_by_docid('articles', docid)

    def get_by_url(self, index, url):
        body = {
            "query": {
                "match": {
                    "url": url
                }
            }
        }
        output = super(ArticleHandler, self).execute_search(index, body)
        return output[0]

    def get_field_with_value(self, index, field, value):
        body = {
            "size": 10000,
             "query": {
                "match": {
                    field: value
                }
             }
        }
        return super(ArticleHandler, self).execute_search(index, body)

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
        return super(ArticleHandler, self).execute_search('articles', body)
