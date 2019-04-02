import sys
import time
import logging

from dart.handler.elastic.connector import ElasticsearchConnector
from dart.handler.elastic.article_handler import ArticleHandler
from dart.handler.other.facebook import RetrieveFacebook


class PopularityQueue:

    """
    Queries the Facebook Graph API for the number of times this URL was shared, and adds this metric to the document
    in Elasticsearch.

    Facebook limits the Graph API at 200 requests per half hour, so this process takes a long time. Since every blocked
    request also counts as a request, the process sleeps for 1800 seconds whenever a block is encountered.
    """

    connector = ElasticsearchConnector()
    searcher = ArticleHandler(connector)
    facebook_handler = RetrieveFacebook()
    module_logging = logging.getLogger('popularity')

    def get_all_documents_without_popularity(self):
        return self.searcher.get_not_calculated('popularity.facebook_share')

    def add_popularity(self, docid, share_count, comment_count):
        self.module_logging.info("Share count: %d, Comment count: %d" % (share_count, comment_count))
        body = {
            "doc": {"popularity": {"facebook_share": int(share_count), "facebook_comment": int(comment_count)}}}
        self.connector.update_document('articles', '_doc', docid, body)

    def execute(self):
        documents = self.get_all_documents_without_popularity()
        while len(documents) > 0:
            for article in documents:
                try:
                    comment_count, share_count = self.facebook_handler.get_facebook_info(article.url)
                    self.add_popularity(article.id, share_count, comment_count)
                    time.sleep(2)
                except KeyError:
                    self.module_logging.error("URL not found; "+article.title)
                    self.add_popularity(article.id, 0, 0)
                    continue
            documents = self.get_all_documents_without_popularity()


def main(argv):
    pq = PopularityQueue()
    pq.execute()


if __name__ == "__main__":
    main(sys.argv[1:])
