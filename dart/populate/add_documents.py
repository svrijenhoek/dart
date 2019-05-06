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

    def __init__(self, folder):
        self.root = folder
        self.connector = ElasticsearchConnector()
        self.searcher = ArticleHandler(self.connector)

        self.count_total = 0
        self.count_fault = 0
        self.count_success = 0

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

        if 'id' not in doc:
            try:
                doc_id = Util.generate_hash(doc['title'] + doc['publication_date'])
                doc['id'] = doc_id
            except KeyError:
                return -1

        body = json.dumps(doc)
        module_logger.info('Added document: '+doc['title'])
        self.connector.add_document('articles', '_doc', body)
        return 1

    def execute(self):
        # iterate over all the files in the data folder
        for path, _, files in os.walk(self.root):
            for name in files:
                # assumes all files are json-l, change this to something more robust!
                for line in open((os.path.join(path, name))):
                    self.count_total += 1
                    json_doc = json.loads(line)
                    success = self.add_document(json_doc)
                    self.count_total += 1
                    if success == 1:
                        self.count_success += 1
                    else:
                        self.count_fault += 1

        module_logger.info("Total number of documents: "+str(self.count_total))
        module_logger.info("Errors: "+str(self.count_fault))
        module_logger.info("Success: "+str(self.count_success))
