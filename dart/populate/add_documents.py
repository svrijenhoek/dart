import json
import csv
import os
import time
import logging
from urllib import request, error
from bs4 import BeautifulSoup
import datetime

from dart.handler.elastic.connector import ElasticsearchConnector
from dart.handler.elastic.article_handler import ArticleHandler
import dart.handler.NLP.annotator
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
        self.language = config['language']
        self.annotator = dart.handler.NLP.annotator.Annotator(self.language)
        self.alternative_schema = config["articles_schema"]
        if self.alternative_schema == "Y":
            self.schema = Util.read_json_file(config["articles_schema_location"])
        self.queue = []

    def request(self, url):
        try:
            fp =request.urlopen(url)
            mybytes = fp.read()
            mystr = mybytes.decode("utf8")
            fp.close()
            return mystr
        except error.HTTPError:
            time.sleep(5)
            return self.request(url)

    @staticmethod
    def read(data):
        soup = BeautifulSoup(data, 'lxml')
        date = soup.find('time').text
        try:
            text = soup.find('section', class_="articlebody").text
        except AttributeError:
            try:
                text = soup.find('div', class_="body-text").text
            except AttributeError:
                try:
                    text = soup.find('div', class_="video-description").text
                except AttributeError:
                    text = ''
        return date, text

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
        self.queue.append(doc)

    def execute(self):

        success = 0
        no_text = 0

        # iterate over all the files in the data folder
        for path, _, files in os.walk(self.root):
            for name in files:
                # assumes all files are json-l, change this to something more robust!
                for line in open((os.path.join(path, name))):
                    json_doc = json.loads(line)
                    if self.alternative_schema == "Y":
                        json_doc = Util.transform(json_doc, self.schema)
                    if 'text' in json_doc and \
                            not "Nutzen Sie gerne die Suche, um zum gewünschten Inhalt zu gelangen." in json_doc['text']:
                        self.add_document(json_doc)
                        success += 1
                    else:
                        no_text += 1
                    if len(self.queue) > 0 and len(self.queue) % 200 == 0:
                        self.connector.add_bulk('articles', '_doc', self.queue)
                        self.queue = []
        if self.queue:
            self.connector.add_bulk('articles', '_doc', self.queue)

        print("\tDocuments successfuly added: {}".format(success))
        print("\tDocuments without text: {}".format(no_text))

    def execute_tsv(self, file_location):
        success = 0
        no_text = 0

        tsv_file = open(file_location, encoding="utf-8")
        read_tsv = csv.reader(tsv_file, delimiter="\t")

        for line in read_tsv:
            if not self.searcher.get_field_with_value('newsid', line[0]):
                json_doc = {'newsid': line[0],
                            'category': line[1],
                            'subcategory': line[2],
                            'title': line[3],
                            'abstract': line[4],
                            'url': line[5],
                }
                try:
                    json_doc['title_entities'] = line[6]
                    json_doc['abstract_entities'] = line[7]
                except IndexError:
                    continue
                data = self.request(json_doc['url'])
                date, text = self.read(data)
                if date and text:
                    _, entities, tags = self.annotator.annotate(text)
                    date = datetime.datetime.strptime(date.replace("/", "-").strip(), '%m-%d-%Y')
                    json_doc['publication_date'] = date.strftime("%Y-%m-%d")
                    json_doc['text'] = text
                    json_doc['tags'] = tags
                    json_doc['entities'] = entities
                    self.add_document(json_doc)
                    success += 1
                else:
                    no_text += 1
                    print(json_doc['url'])
                if len(self.queue) > 0 and len(self.queue) % 200 == 0:
                    self.connector.add_bulk('articles', '_doc', self.queue)
                    self.queue = []
        if self.queue:
            self.connector.add_bulk('articles', '_doc', self.queue)



