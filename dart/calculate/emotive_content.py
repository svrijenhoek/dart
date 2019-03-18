from dart.handler.elastic.article_handler import ArticleHandler
from dart.models.Article import Article
import pandas as pd
import spacy

# relativity_words = {'gebied', 'gaan', 'buigen'}
# negation = ['niet', 'geen', 'nooit', 'niets', 'niemand', 'nergens']
spacy_tags = ['DET', 'ADP', 'PRON']


class IdentifyEmotiveContent:

    def __init__(self):
        self.searcher = ArticleHandler()
        self.nlp = spacy.load('nl_core_news_sm', disable=['parser', 'ner'])

    def execute(self):
        for x in range(0, 100):
            document = Article(self.searcher.get_random_article())
            print(document.title)
            print(document.doctype)
            doc = self.nlp(document.text)
            tags = [token.pos_ for token in doc]
            s = pd.Series(tags)
            counts = s.value_counts()

            # TO DO: implement adding to Elasticsearch
            for tag in spacy_tags:
                try:
                    count = counts[tag]
                    percentage = count/len(s)
                    print('{}:\t{}'.format(tag, percentage))
                except KeyError:
                    print('{}:\t{}'.format(tag, 0))
            print()
