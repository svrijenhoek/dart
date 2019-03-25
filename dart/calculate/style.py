from dart.models.Article import Article
from dart.models.Recommendation import Recommendation
from dart.models.User import User
from dart.handler.elastic.user_handler import UserHandler
from dart.handler.elastic.article_handler import ArticleHandler
from dart.handler.elastic.recommendation_handler import RecommendationHandler
from dart.handler.elastic.connector import Connector
import pandas as pd
import json


class AggregateRecommendations:

    def __init__(self):
        self.connector = Connector()
        self.user_handler = UserHandler()
        self.article_handler = ArticleHandler()
        self.recommendation_handler = RecommendationHandler()
        self.users = self.user_handler.get_all_users()

    def retrieve_recommendations(self, user_id):
        columns = ["id", "date", "recommendation_type", "popularity", "complexity", "nwords", "nsentences"]
        recommended_articles = self.recommendation_handler.get_recommendations_to_user(user_id)
        table = []
        for ra in recommended_articles:
            recommendation = Recommendation(ra)
            article = Article(self.article_handler.get_by_id(recommendation.article['id']))
            row = [article.id, recommendation.date, recommendation.type, article.popularity, article.complexity,
                      article.nwords, article.nsentences]
            table.append(row)
        df = pd.DataFrame(table, columns=columns)
        return df

    def get_averages(self, df):
        avg_complexity = self.calculate_average(df, 'complexity')
        avg_popularity = self.calculate_average(df, 'popularity')
        avg_nwords = self.calculate_average(df, 'nwords')
        avg_nsentences = self.calculate_average(df, 'nsentences')
        return [avg_popularity, avg_complexity, avg_nwords, avg_nsentences]

    @staticmethod
    def calculate_average(df, column):
        return df.loc[:, column].mean()

    def add_document(self, user_id, range, date, recommendation_type, metrics):
        doc = {
            'user': user_id,
            'range': range,
            'date': date,
            'type': recommendation_type,
            'avg_popularity': metrics[0],
            'avg_complexity': metrics[1],
            'avg_nwords': metrics[2],
            'avg_nsentences': metrics[3]
        }
        body = json.dumps(doc)
        self.connector.add_document('aggregated_recommendations', '_doc', body)

    def execute(self):
        # iterate over all recommendations generated for all users
        for entry in self.users:
            user = User(entry)
            df = self.retrieve_recommendations(user.id)
            recommendation_types = df.recommendation_type.unique()
            # do for all recommendation types separately
            for recommendation_type in recommendation_types:
                articles = df[(df.recommendation_type == recommendation_type)]
                # calculate yearly averages
                averages = self.get_averages(articles)
                self.add_document(user.id, 'year', '31-12-2017', recommendation_type, averages)
                # calculate monthly averages
                dates = articles.date.unique()
                for date in dates:
                    articles_per_date = articles[(articles.date == date)]
                    averages = self.get_averages(articles_per_date)
                    self.add_document(user.id, 'month', date, recommendation_type, averages)

