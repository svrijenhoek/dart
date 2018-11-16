import sys
import urllib
import json
import time

from Elastic.Connector import Connector
from Elastic.Search import Search


class PopularityQueue:

    facebook_graph_url = 'https://graph.facebook.com/?id='

    connector = Connector()
    searcher = Search()

    def get_all_documents_without_popularity(self):
        return self.searcher.get_popularity_not_calculated()

    def get_facebook_info(self, url):
        page = urllib.request.urlopen(self.facebook_graph_url + url)
        content = json.loads(page.read())
        comments = content['share']['comment_count']
        shares = content['share']['share_count']
        return comments, shares

    def update_document(self, docid, share_count, comment_count):
        print("Share count: %d, Comment count: %d" % (share_count, comment_count))
        body = {
            "doc": {"popularity": {"facebook_share": int(share_count), "facebook_comment": int(comment_count)}}}
        self.connector.update_document('articles', 'text', docid, body)

    def execute(self, documents):
        for doc in documents:
            try:
                url = doc['_source']['url']
                docid = doc['_id']

                comment_count, share_count = self.get_facebook_info(url)
                self.add_popularity(docid, share_count, comment_count)
                time.sleep(2)
            except KeyError:
                print("URL not found")
                continue
            except urllib.error.HTTPError:
                print("Graph API limit reached")
                time.sleep(1800)


def main():
    more_documents = True
    while more_documents:
        pq = PopularityQueue()
        documents = pq.get_all_documents_without_popularity()
        pq.execute(documents)
        if len(documents) < 10000:
            more_documents = False


if __name__ == "__main__":
    main(sys.argv[1:])
