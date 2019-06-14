from dart.handler.elastic.base_handler import BaseHandler
from dart.models.Article import Article


class ArticleHandler(BaseHandler):

    """
    Data handler for all articles. Returns lists of Articles, and adds documents to Elasticsearch.
    Standard queries for:
    - random document
    - all documents (with scroll, should be managed from calculation classes
    - documents where certain fields are still empty
    ....
    """

    def __init__(self, connector):
        super(ArticleHandler, self).__init__(connector)
        self.connector = connector

    def add_document(self, doc):
        self.connector.add_document('articles', '_doc', doc)

    def update(self, docid, field, value):
        body = {
            "doc": {field: value}
        }
        self.connector.update_document('articles', '_doc', docid, body)

    def update_bulk(self, docs):
        self.connector.update_bulk('articles', docs)

    def update_doc(self, docid, doc):
        body = {
            "doc": doc
        }
        self.connector.update_document('articles', '_doc', docid, body)

    def add_field(self, docid, field, value):
        body = {
            "doc": {field: value}}
        self.connector.update_document('articles', '_doc', docid, body)

    def get_not_calculated(self, field):
        """
        returns the articles that have a certain field not populated. This is used for example when calculating the
        popularity of articles.
        """
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
        response = self.connector.execute_search('articles', body)
        return [Article(i) for i in response]

    def get_most_popular(self, size):
        """
        returns all articles that have been shared on Facebook most often
        """
        body = {
            "size": size,
            "sort": [
                {"popularity.facebook_share": {"order": "desc", "mode": "max", "unmapped_type": "long"}}
            ],
            "query": {
                "match_all": {},
            }}
        response = self.connector.execute_search('articles', body)
        return [Article(i) for i in response]

    def get_random_article(self):
        """
        Returns a random article
        """
        return Article(super(ArticleHandler, self).get_random('articles'))

    def get_similar_documents(self, docid, size):
        """
        given a document id, retrieve the documents that are most similar to it according to Elastic's
        More Like This functionality.
        """
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
            }}
        }
        response = self.connector.execute_search('articles', body)
        return [Article(i) for i in response]

    def get_all_in_timerange(self, l, u):
        lower = l.strftime('%Y-%m-%dT%H:%M:%S')
        upper = u.strftime('%Y-%m-%dT%H:%M:%S')
        docs = []
        body = {
            'query': {"range": {
                "publication_date": {
                    "lt": upper,
                    "gte": lower
                }
            }},
            "sort": [
                {"popularity.facebook_share": {"order": "desc", "mode": "max", "unmapped_type": "long"}}
            ]
        }
        sid, scroll_size = self.connector.execute_search_with_scroll('articles', body)
        # Start retrieving documents
        while scroll_size > 0:
            result = self.connector.scroll(sid, '2m')
            sid = result['_scroll_id']
            scroll_size = len(result['hits']['hits'])
            for hit in result['hits']['hits']:
                docs.append(hit)
        return [Article(i) for i in docs]

    # get elastic entry by id
    def get_by_id(self, docid):
        return Article(super(ArticleHandler, self).get_by_docid('articles', docid))

    def get_by_url(self, index, url):
        body = {
            "query": {
                "match": {
                    "url": url
                }
            }
        }
        output = self.connector.execute_search(index, body)
        return Article(output[0])

    def get_field_with_value(self, field, value):
        body = {
            "size": 10000,
            "query": {
                "match": {
                    field: value
                }
             }
        }
        response = self.connector.execute_search('articles', body)
        return [Article(i) for i in response]

    def more_like_this_history(self, reading_history, upper, lower):
        """
        used in the 'more like this' recommendation generator. Finds more articles based on the users reading history
        """

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
        response = self.connector.execute_search('articles', body)
        return [Article(i) for i in response]
