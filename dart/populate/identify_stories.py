import dart.handler.elastic.connector
import dart.models.Handlers
import dart.handler.NLP.cosine_similarity
import dart.Util
from datetime import datetime, timedelta
import pandas as pd
import networkx as nx
import community
from collections import defaultdict
from statistics import mode, StatisticsError

import itertools
from difflib import SequenceMatcher


class StoryIdentifier:
    """
    Class that aims to identify news stories in a set of news articles according to the principles noted in
    Nicholls et al.

    Currently only looks at articles from the same day, needs to be expanded.
    """

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config
        self.cos = dart.handler.NLP.cosine_similarity.CosineSimilarity(self.config['language'])
        self.threshold = 0.25

    def execute(self):
        first_date = datetime.strptime(self.config["recommendation_dates"][0], '%d-%m-%Y')
        last_date = datetime.strptime(self.config["recommendation_dates"][-1], '%d-%m-%Y')
        delta = last_date - first_date

        cosines = []
        for i in range(delta.days+1):
            today = first_date + timedelta(days=i)
            print(today)
            yesterday = today - timedelta(days=1)
            past_three_days = today - timedelta(days=3)
            documents_3_days = self.handlers.articles.get_all_in_timerange(past_three_days, today)
            documents_1_day = self.handlers.articles.get_all_in_timerange(yesterday, today)
            for x in documents_1_day:
                for y in documents_3_days:
                    cosine = self.cos.calculate_cosine_similarity(x.id, y.id)
                    if cosine > 0:
                        cosines.append({'x': x.id, 'y': y.id, 'cosine': cosine})
        stories = self.identify(cosines)
        self.add_stories(stories)

        # stories = self.identify(documents)
        # self.add_stories(today.strftime("%d-%m-%Y"), stories, documents)

    def identify(self, cosines):
        # calculate cosine similarity between documents
        # ids = [article.id for article in documents if not article.text == '']
        # cosines = self.cos.calculate_all_distances(ids)
        # if cosines:
        df = pd.DataFrame(cosines)
        df = df.drop_duplicates()
        # filter too-low similarities in order not to confuse the clustering algorithm
        over_threshold = df[df.cosine > self.threshold]
        # create graph
        G = nx.from_pandas_edgelist(over_threshold, 'x', 'y', edge_attr='cosine')
        # create partitions, or stories
        partition = community.best_partition(G)
        return partition
        # else:
        #    return {}

    def update_articles(self, stories, documents):
        docs = [{'id': doc_id, 'story': story_id} for doc_id, story_id in stories.items()]
        self.handlers.articles.update_bulk(docs)

        count = len(stories)
        documents_in_stories = [docid for docid in stories.keys()]
        all_documents = [doc.id for doc in documents]
        single_articles = sorted(set(all_documents).difference(documents_in_stories))
        docs = []
        for article in single_articles:
            docs.append({'id': article, 'story': count})
            count += 1
        self.handlers.articles.update_bulk(docs)

    def print_stories(self, stories, documents):
        v = defaultdict(list)
        for key, value in stories.items():
            v[value].append(key)
        for key, value in v.items():
            print(key)
            print(self.cos.most_relevant_terms(value))
            classifications = []
            titles = []
            for docid in value:
                article = self.handlers.articles.get_by_id(docid)
                titles.append(article.title)
                classifications.append(article.classification)
            try:
                print(mode(classifications))
            except StatisticsError:
                print(classifications)
            for title in titles:
                print("\t" + title)
        count = len(stories)
        documents_in_stories = [docid for docid in stories.keys()]
        all_documents = [doc.id for doc in documents]
        single_articles = sorted(set(all_documents).difference(documents_in_stories))
        for article_id in single_articles:
            article = self.handlers.articles.get_by_id(article_id)
            print("{}\t{}".format(count, article.title))
            count += 1

    def add_stories(self, stories):
        s = defaultdict(list)
        # make a dictionary where each story id is linked to its article ids
        for k, v in stories.items():
            s[v].append(k)
        # identify the most important keywords, most common classification and a title
        for story_id, doc_ids in s.items():
            keywords = self.cos.most_relevant_terms(doc_ids)
            classifications = []
            titles = []
            dates = []
            for doc_id in doc_ids:
                article = self.handlers.articles.get_by_id(doc_id)
                classifications.append(article.classification)
                titles.append(article.title)
                dates.append(article.publication_date)
            try:
                classification = mode(classifications)
            except StatisticsError:
                classification = classifications[0]
            self.handlers.stories.add_to_queue(dates[0], dates, story_id, doc_ids, keywords, classification, titles[0])

        # account for all the documents that are not part of stories
        # disabled during refactoring
        count = len(stories)
        documents_in_stories = [docid for docid in stories.keys()]
        all_documents = [doc.id for doc in self.handlers.articles.get_all_articles()]
        single_articles = sorted(set(all_documents).difference(documents_in_stories))
        for article_id in single_articles:
            article = self.handlers.articles.get_by_id(article_id)
            keywords = self.cos.most_relevant_terms([article_id])
            self.handlers.stories.add_to_queue(article.publication_date, article.publication_date, count, article.id, keywords, article.classification, article.title)
            count += 1
        self.handlers.stories.add_bulk()

    @staticmethod
    def distance(names):
        output = []
        for a, b in itertools.combinations(names, 2):
            if len(a) < 3 or len(b) < 3:
                similarity = 0
            elif a in b or b in a:
                similarity = 1
            else:
                similarity = SequenceMatcher(None, a, b).ratio()
            output.append({'a': a, 'b': b, 'similarity': similarity})
        return output
