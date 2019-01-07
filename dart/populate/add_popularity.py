import sys
import urllib
import json
import time

from dart.helper.elastic.connector import Connector
from dart.helper.elastic.querybuilder import QueryBuilder
from dart.models.Article import Article


class PopularityQueue:

    """
    Queries the Facebook Graph API for the number of times this URL was shared, and adds this metric to the document
    in Elasticsearch.

    Facebook limits the Graph API at 200 requests per half hour, so this process takes a long time. Since every blocked
    request also counts as a request, the process sleeps for 1800 seconds whenever a block is encountered.
    """

    facebook_graph_url = 'https://graph.facebook.com/?id='

    connector = Connector()
    searcher = QueryBuilder()

    def get_all_documents_without_popularity(self):
        return self.searcher.get_not_calculated('popularity.facebook_share')

    def get_facebook_info(self, url):
        page = urllib.request.urlopen(self.facebook_graph_url + url)
        content = json.loads(page.read())
        comments = content['share']['comment_count']
        shares = content['share']['share_count']
        return comments, shares

    def add_popularity(self, docid, share_count, comment_count):
        print("Share count: %d, Comment count: %d" % (share_count, comment_count))
        body = {
            "doc": {"popularity": {"facebook_share": int(share_count), "facebook_comment": int(comment_count)}}}
        self.connector.update_document('articles', '_doc', docid, body)

    def execute(self, documents):
        for document in documents:
            article = Article(document)
            try:
                comment_count, share_count = self.get_facebook_info(article.url)
                self.add_popularity(article.id, share_count, comment_count)
                time.sleep(2)
            except KeyError:
                print("URL not found")
                continue
            except urllib.error.HTTPError:
                print("Graph API limit reached")
                time.sleep(1800)


def main(argv):
    more_documents = True
    while more_documents:
        pq = PopularityQueue()
        documents = pq.get_all_documents_without_popularity()
        pq.execute(documents)
        if len(documents) < 10000:
            more_documents = False


if __name__ == "__main__":
    main(sys.argv[1:])
