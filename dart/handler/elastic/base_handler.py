from dart.handler.elastic.connector import Connector
import time


class BaseHandler(Connector):

    def __init__(self):
        super(Connector, self).__init__()

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
        return super(BaseHandler, self).execute_search(index, body)[0]