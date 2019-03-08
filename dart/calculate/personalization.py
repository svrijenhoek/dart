from dart.handler.elastic.article_handler import ArticleHandler
from dart.handler.elastic.connector import Connector
import pandas as pd
import numpy as np
import difflib
import sys
import json


# Class to calculate the overall personalisation for each individual user
# Retrieves all recommendations made, and calculates the similarity between them per date

class Personalization:

    def __init__(self):
        self.searcher = ArticleHandler()
        self.connector = Connector()

    # retrieves all recommendations found in the elasticsearch index
    def initialize(self):
        recommendations = self.searcher.get_all_documents('recommendations')
        table = []
        for rec in recommendations:
            source = rec['_source']
            row = [source['user_id'], source['date'],
                   source['recommendations']]
            table.append(row)
        columns = ['user_id', 'date', 'recommendations']
        return pd.DataFrame(table, columns=columns)

    # combine all found similarities into one overall similarity average per user
    # output is added to elasticsearch index
    def analyze(self, df):
        headers = list(df.columns.values)
        headers = [e for e in headers if e not in ('date', 'user_id')]

        users = df.user_id.unique()
        for user in users:
            df1 = df[(df.user_id == user)]
            for header in headers:
                # per user mean
                mean = np.mean(df1[header])
                self.add_document(user, header, mean)

    # construct the json document that can be added to the elasticsearch index
    def add_document(self, user, header, mean):
        doc = {
            'user': user,
            'type': header,
            'mean': mean,
        }
        body = json.dumps(doc)
        self.connector.add_document('personalization', '_doc', body)

    # calculates for lists x and y how many elements they have in common
    # output: 0..1, where 1 is a complete match and 0 is no match at all
    @staticmethod
    def calculate_similarity(x, y):
        sm = difflib.SequenceMatcher(None, x, y)
        return sm.ratio()

    # function to compare the recommendations of each user with those of all other users and return their commonality
    # output: table where each row contains a user_id, the date, and the similarity to one other recommendation
    def compare_recommendations(self, date, df):
        table = []
        for index_x, row_x in df.iterrows():
            recommendation_types = row_x.recommendations.keys()
            for index_y, row_y in df.iterrows():
                row = {'user_id': row_x.user_id, 'date': date}
                for key in recommendation_types:
                    x = row_x.recommendations[key]
                    y = row_y.recommendations[key]
                    row[key] = self.calculate_similarity(x, y)
                table.append(row)
        return table

    def execute(self):
        # retrieve all recommendations
        df = self.initialize()
        # compare recommendations per date
        dates = df.date.unique()
        table = []
        for date in dates:
            df1 = df[(df.date == date)]
            output = self.compare_recommendations(date, df1)
            table = table + output
        output = pd.DataFrame.from_dict(table)
        # analyze the overall means
        self.analyze(output)


def main(argv):
    personalization = Personalization()
    personalization.execute()


if __name__ == "__main__":
    main(sys.argv[1:])
