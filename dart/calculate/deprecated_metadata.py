import sys
import numpy as np
import pandas as pd
from dart.helper.elastic.querybuilder import QueryBuilder
from dart.helper.NLP.cosine_similarity import CosineSimilarity
from dart.models.Recommendation import Recommendation
from dart.models.Article import Article


class Calculations:

    searcher = QueryBuilder()
    recommendations = []
    cs = CosineSimilarity()

    def __init__(self):
        print("INITIALIZING")
        # prepare tables
        source_table = []
        popularity_table = []
        cosine_table = []
        recommendations = [Recommendation(i) for i in self.searcher.get_all_documents('recommendations')]
        for rec in recommendations:
            for type in rec.get_recommendation_types():
                date = rec.date
                for docid in rec.get_articles_for_type(type):
                    document = Article(self.searcher.get_by_id('articles', docid))
                    source_table.append([date, type, document.doctype])
                    popularity_table.append([date, type, document.popularity])
                    cosine_table.append([date, type, docid])
        # transform tables into dataframes
        self.source_df = pd.DataFrame(source_table)
        self.source_df.columns = ['date', 'recommender', 'source']
        self.popularity_df = pd.DataFrame(popularity_table)
        self.popularity_df.columns = ['date', 'recommender', 'shares']
        self.cosine_df = pd.DataFrame(cosine_table)
        self.cosine_df.columns = ['date', 'recommender', 'id']

    # create function for calculating source spread
    def calculate_source_spread(self):
        df = self.source_df
        for value in df.recommender.unique():
            slice = df[(df.recommender == value)]
            print(value)
            print(slice.source.describe())
            print()

    # create function for calculating popularity spread
    def calculate_popularity_spread(self):
        df = self.popularity_df
        for value in df.recommender.unique():
            slice = df[(df.recommender == value)]
            print(value)
            print(slice.shares.describe())

    # create function for calculating cosine similarity spread
    def calculate_cosine_spread(self):
        df = self.cosine_df
        for recommender in df.recommender.unique():
            averages = []
            print(recommender)
            slice = df[(df.recommender == recommender)]
            for date in slice.date.unique():
                df2 = slice[(slice.date == date)]
                text_ids = df2.id
                output = self.cs.calculate_cosine_similarity(text_ids)
                if not len(output) == 0:
                    averages.append(np.mean(output))
            print(np.mean(averages))
            print(averages)

    def execute(self):
        print("SOURCE SPREAD")
        self.calculate_source_spread()
        print("POPULARITY SPREAD")
        self.calculate_popularity_spread()
        print("COSINE SPREAD")
        self.calculate_cosine_spread()


def main(argv):
    calculations = Calculations()
    calculations.execute()


if __name__ == "__main__":
    main(sys.argv[1:])
