import sys
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


class StoryIdentifier:

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config
        self.cos = dart.handler.NLP.cosine_similarity.CosineSimilarity()
        self.threshold = 0.25

    def execute(self):
        for date in self.config["recommendation_dates"]:
            upper_date = datetime.strptime(date, '%d-%m-%Y')
            lower_date = upper_date - timedelta(days=self.config["recommendation_range"])
            documents = self.handlers.articles.get_all_in_timerange(lower_date, upper_date)
            stories = self.identify(documents)
            # self.update_articles(stories, documents)
            self.add_stories(date, stories, documents)

    def identify(self, documents):
        # calculate cosine similarity between documents
        cosines = self.cos.calculate_all(documents)
        df = pd.DataFrame(cosines)
        # filter too-low similarities in order not to confuse the clustering algorithm
        over_threshold = df[df.cosine > self.threshold]
        # create graph
        G = nx.from_pandas_edgelist(over_threshold, 'x', 'y', edge_attr='cosine')
        # create partitions, or stories
        partition = community.best_partition(G)
        return partition

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

    def add_stories(self, date, stories, documents):
        v = defaultdict(list)
        for key, value in stories.items():
            v[value].append(key)
        for key, value in v.items():
            keywords = self.cos.most_relevant_terms(value)
            classifications = []
            titles = []
            for docid in value:
                article = self.handlers.articles.get_by_id(docid)
                classifications.append(article.classification)
                titles.append(article.title)
            try:
                classification = mode(classifications)
            except StatisticsError:
                classification = classifications[0]
            self.handlers.stories.add_to_queue(date, key, value, keywords, classification, titles[0])

        count = len(stories)
        documents_in_stories = [docid for docid in stories.keys()]
        all_documents = [doc.id for doc in documents]
        single_articles = sorted(set(all_documents).difference(documents_in_stories))
        for article_id in single_articles:
            article = self.handlers.articles.get_by_id(article_id)
            keywords = self.cos.most_relevant_terms([article_id])
            self.handlers.stories.add_to_queue(date, count, article.id, keywords, article.classification, article.title)
            count += 1
        self.handlers.stories.add_bulk()
