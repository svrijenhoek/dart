from dart.handler.elastic.article_handler import ArticleHandler
from dart.models.Article import Article
import pandas as pd
import spacy


class IdentifyEmotiveContent:

    def __init__(self):
        self.searcher = ArticleHandler()
        self.nlp = spacy.load('nl_core_news_sm', disable=['parser', 'ner'])
        self.spacy_tags = ['DET', 'ADP', 'PRON']

    def calculate(self, s):
        """
        calculates for each tag specified its representation in the selected article
        """
        counts = s.value_counts()
        result = {}
        for tag in self.spacy_tags:
            try:
                count = counts[tag]
                percentage = count / len(s)
                result[tag] = percentage
            except KeyError:
                result[tag] = 0
        return result

    def execute(self):
        # TO DO: REWRITE FOR ALL RECOMMENDATIONS
        for _ in range(0, 100):
            document = Article(self.searcher.get_random_article())
            tags = document.tags
            s = pd.Series(tags)
            percentages = self.calculate(s)
            # TO DO: implement adding to Elasticsearch
            print(percentages)

