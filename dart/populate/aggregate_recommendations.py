from dart.models.Article import Article
from dart.helper.elastic.querybuilder import QueryBuilder
from dart.helper.elastic.connector import Connector
import pandas as pd
import json

import sys


class AggregateRecommendations:

    def __init__(self):
        self.connector = Connector()
        self.searcher = QueryBuilder()
        self.users = self.searcher.get_all_documents('users')

    def retrieve_recommendations(self, user_id):
        columns = ["id", "date", "type", "popularity", "complexity", "nwords", "nsentences"]
        recommended_articles = self.searcher.get_field_with_value('recommended_articles', 'recommendation.user_id', user_id)
        table = []
        for ra in recommended_articles:
            recommendation_type = ra['_source']['recommendation']['type']
            recommendation_date = ra['_source']['recommendation']['date']
            article = Article(self.searcher.get_by_id('articles', ra['_source']['article']['id']))
            row = [article.id, recommendation_date, recommendation_type, article.popularity, article.complexity,
                   article.nwords, article.nsentences]
            table.append(row)
        df = pd.DataFrame(table, columns=columns)
        return df

    def get_metrics(self, df):
        avg_complexity = self.calculate_average(df, 'complexity')
        avg_popularity = self.calculate_average(df, 'popularity')
        avg_nwords = self.calculate_average(df, 'nwords')
        avg_nsentences = self.calculate_average(df, 'nsentences')
        return [avg_popularity, avg_complexity, avg_nwords, avg_nsentences]

    @staticmethod
    def calculate_average(df, column):
        return df.loc[:, column].mean()

    def add_document(self, user_id, range, date, type, metrics):
        doc = {
            'user': user_id,
            'range': range,
            'date': date,
            'type': type,
            'avg_popularity': metrics[0],
            'avg_complexity': metrics[1],
            'avg_nwords': metrics[2],
            'avg_nsentences': metrics[3]
        }
        body = json.dumps(doc)
        self.connector.add_document('aggregated_recommendations', '_doc', body)

    def execute(self):
        for user in self.users:
            print(user['_id'])
            df = self.retrieve_recommendations(user['_id'])
            types = df.type.unique()
            for type in types:
                articles_per_type = df[(df.type == type)]
                year_metrics = self.get_metrics(articles_per_type)
                self.add_document(user['_id'], 'year', '31-12-2017', type, year_metrics)
                dates = articles_per_type.date.unique()
                for date in dates:
                    print(date)
                    articles_per_date = articles_per_type[(articles_per_type.date == date)]
                    month_metrics = self.get_metrics(articles_per_date)
                    self.add_document(user['_id'], 'month', date, type, month_metrics)


def main(argv):
    run = AggregateRecommendations()
    run.execute()


if __name__ == "__main__":
    main(sys.argv[1:])
