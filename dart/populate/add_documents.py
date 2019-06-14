import json
import os
import logging

from dart.handler.elastic.connector import ElasticsearchConnector
from dart.handler.elastic.article_handler import ArticleHandler
import dart.Util as Util

module_logger = logging.getLogger('add_documents')


class AddDocuments:

    """
    Class that adds articles into an ElasticSearch index. Articles are first annotated using spaCy's tagger and
    Named Entity Recognizer.
    By default, if no popularity metric is specified, it is set to 'no'.
    """

    def __init__(self, config):
        self.root = config['articles_folder']
        self.connector = ElasticsearchConnector()
        self.searcher = ArticleHandler(self.connector)
        self.alternative_schema = config["articles_schema"]
        if self.alternative_schema == "Y":
            self.schema = Util.read_json_file(config["articles_schema_location"])
        self.queue = []

    def add_document(self, doc):
        # see if the user has specified their own id. If this is the case, use this in Elasticsearch,
        # otherwise generate a new one based on the title and publication date
        # TO DO: see if this is necessary!
        try:
            doc['text'] = doc['text'].replace('|', ' ')
        except KeyError:
            return -1
        try:
            del doc['htmlsource']
        except KeyError:
            pass

        body = json.dumps(doc)
        self.queue.append(body)

    def execute(self):
        # iterate over all the files in the data folder
        for path, _, files in os.walk(self.root):
            for name in files:
                # assumes all files are json-l, change this to something more robust!
                for line in open((os.path.join(path, name))):
                    json_doc = json.loads(line)
                    if self.alternative_schema == "Y":
                        json_doc = Util.transform(json_doc, self.schema)
                    if json_doc:
                        self.add_document(json_doc)
                    if len(self.queue) > 0 and len(self.queue) % 200 == 0:
                        self.connector.add_bulk('articles', '_doc', self.queue)
                        self.queue = []
        if self.queue:
            self.connector.add_bulk('articles', '_doc', self.queue)
