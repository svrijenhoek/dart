import sys
import numpy as np
import pandas as pd
from Elastic.Search import Search
from NLP.CosineSimilarity import CosineSimilarity


class Calculations:

    searcher = Search()
    recommendations = []
    cs = CosineSimilarity()

    def __init__(self):
        all = self.searcher.get_all_documents('recommendations')
        self.recommendations = [
            {'date': i['_source']['date'],
             'types': i['_source']['recommendations']
             } for i in all]

    # create function for calculating source spread
    def calculate_source_spread(self):
        table = []
        for rec in self.recommendations:
            for type in rec['types']:
                date = rec['date']
                recommended_docs = rec['types'][type]
                for docid in recommended_docs:
                    document = self.searcher.get_by_id('articles', docid)
                    table.append([date, type, document['_source']['doctype']])

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
            date = rec['date']
            for type in rec['types']:
                for docid in rec['types'][type]:
                    try:
                        document = self.searcher.get_by_id('articles', docid)
                        table.append([date, type, document['_source']['popularity']['facebook_share']])
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
            date = rec['date']
            for type in rec['types']:
                for docid in rec['types'][type]:
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
        # self.calculate_source_spread()
        print("POPULARITY SPREAD")
        # self.calculate_popularity_spread()
        print("COSINE SPREAD")
        self.calculate_cosine_spread()


def main(argv):
    calculations = Calculations()
    calculations.execute()


if __name__ == "__main__":
    main(sys.argv[1:])