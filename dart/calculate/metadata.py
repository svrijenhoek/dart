import sys
import numpy as np
import pandas as pd
from dart.helper.elastic.querybuilder import QueryBuilder
from dart.helper.NLP.cosine_similarity import CosineSimilarity
from dart.Recommendation import Recommendation
from dart.Article import Article


class Calculations:

    searcher = QueryBuilder()
    recommendations = []
    cs = CosineSimilarity()

    def __init__(self):
        self.recommendations = [Recommendation(i) for i in self.searcher.get_all_documents('recommendations')]

    # create function for calculating source spread
    def calculate_source_spread(self):
        table = []
        for rec in self.recommendations:
            for type in rec.get_recommendation_types():
                date = rec.date
                for docid in rec.get_articles_for_type(type):
                    document = Article(self.searcher.get_by_id('articles', docid))
                    table.append([date, type, document.doctype])

        df = pd.DataFrame(table)
        df.columns = ['date', 'recommender', 'source']
        for value in df.recommender.unique():
            slice = df[(df.recommender == value)]
            print(value)
            print(slice.source.describe())
            print()

    # create function for calculating popularity spread
    def calculate_popularity_spread(self):

        table = []
        for rec in self.recommendations:
            date = rec.date
            for type in rec.get_recommendation_types():
                for docid in rec.get_articles_for_type(type):
                    try:
                        document = Article(self.searcher.get_by_id('articles', docid))
                        table.append([date, type, document.popularity])
                    except KeyError:
                        continue
        df = pd.DataFrame(table)
        df.columns = ['date', 'recommender', 'shares']
        for value in df.recommender.unique():
            slice = df[(df.recommender == value)]
            print(value)
            print(slice.shares.describe())

    # create function for calculating cosine similarity spread
    def calculate_cosine_spread(self):
        table = []
        for rec in self.recommendations:
            date = rec.date
            for type in rec.get_recommendation_types():
                for docid in rec.get_articles_for_type(type):
                    table.append([date, type, docid])

        df = pd.DataFrame(table)
        df.columns = ['date', 'recommender', 'id']
        for recommender in df.recommender.unique():
            averages = []
            print(recommender)
            slice = df[(df.recommender == recommender)]
            for date in slice.date.unique():
                df2 = slice[(slice.date == date)]
                text_ids = df2.id
                output = []
                for x in range(0, len(df2)):
                    for y in range(0, len(df2)):
                        try:
                            cosine = self.cs.calculate_cosine_similarity(text_ids[x], text_ids[y])
                            if cosine < 1:
                                output.append(cosine)
                        except KeyError:
                            continue
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
