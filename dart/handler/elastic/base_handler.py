from dart.handler.elastic.connector import Connector
import time


class BaseHandler(Connector):

    def __init__(self):
        super(BaseHandler, self).__init__()

    # gets a random document from a specified index
    def get_random(self, index):
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
        return super(BaseHandler, self).execute_search(index, body)[0]

    def get_by_docid(self, index, docid):
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
        output = super(BaseHandler, self).execute_search(index, body)
        return output[0]

    def get_all_documents(self, index):
        docs = []
        body = {
            "query": {
                "match_all": {},
            }
        }
        sid, scroll_size = super(BaseHandler, self).execute_search_with_scroll(index, body)
        # Start retrieving documents
        while scroll_size > 0:
            result = super(BaseHandler, self).scroll(sid, '2m')
            sid = result['_scroll_id']
            scroll_size = len(result['hits']['hits'])
            for hit in result['hits']['hits']:
                docs.append(hit)
        return docs
