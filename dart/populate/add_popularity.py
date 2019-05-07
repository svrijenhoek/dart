import sys
import time
import logging
import csv

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

    def add_popularity(self, docid, share_count):
        self.module_logging.info("Share count: %d" % share_count)
        body = {
            "doc": {"popularity": {"facebook_share": int(share_count)}}}
        self.connector.update_document('articles', '_doc', docid, body)

    def execute(self):
        documents = self.get_all_documents_without_popularity()
        while len(documents) > 0:
            for article in documents:
                try:
                    share_count = self.facebook_handler.get_facebook_info(article.url)
                    self.add_popularity(article.id, share_count)
                    time.sleep(2)
                except KeyError:
                    self.module_logging.error("URL not found; "+article.title)
                    self.add_popularity(article.id, 0, 0)
                    continue
            documents = self.get_all_documents_without_popularity()

    def read_from_file(self, file):
        with open(file, mode='r') as csv_file:
            next(csv_file)
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                title = row[3]
                popularity = row[2].replace(',', '')
                article = self.searcher.get_field_with_value('title', title)[0]
                self.searcher.update(article.id, 'popularity.facebook_share', int(popularity))


def main(argv):
    pq = PopularityQueue()
    pq.read_from_file()


if __name__ == "__main__":
    main(sys.argv[1:])
