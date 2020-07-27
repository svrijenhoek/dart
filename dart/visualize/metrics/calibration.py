import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Calibration:

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config

    def calculate_calibration(self, recommendations, reading_history):
        recommendation_articles = self.handlers.articles.get_multiple_by_id(recommendations)
        reading_history_articles = self.handlers.articles.get_multiple_by_id(reading_history)
        # calculate topics divergence
        topics_divergence = self.calculate_categorical_divergence(
            [article.editorialTags for article in recommendation_articles],
            [article.editorialTags for article in reading_history_articles]
        )
        # calculate complexity divergence
        complexity_divergence = self.calculate_numerical_divergence(
            [article.complexity for article in recommendation_articles],
            [article.complexity for article in reading_history_articles]
        )
        return topics_divergence, complexity_divergence

    @staticmethod
    def calculate_categorical_divergence(l1, l2):
        return 1

    @staticmethod
    def calculate_numerical_divergence(l1, l2):
        return abs(np.mean(l1) - np.mean(l2))

    @staticmethod
    def visualize(df):
        print(df.groupby('type')['complexity'].mean())
        print(df.groupby('type')['topics'].mean())
        plt.figure()
        df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")
        df = df.sort_values('date', ascending=True)
        df.set_index('date', inplace=True)
        df.groupby('type')['complexity'].plot(legend=True)
        plt.xticks(rotation='vertical')
        plt.draw()

    def execute(self):
        data = []
        users = self.handlers.users.get_all_users()
        if self.config['test_size'] > 0:
            users = users[1:self.config['test_size']]
        for date in self.config["recommendation_dates"]:
            print(date)
            calibration_topics = []
            calibration_complexity = []
            for recommendation_type in self.handlers.recommendations.get_recommendation_types():
                for user in users:
                    recommendation = self.handlers.recommendations.get_recommendations_to_user_at_date(
                        user.id,
                        date,
                        recommendation_type)
                    if recommendation:
                        reading_history = user.select_reading_history(date, recommendation_type)
                        c_topics, c_complexity = self.calculate_calibration(recommendation[0].articles, reading_history)
                        calibration_topics.append(c_topics)
                        calibration_complexity.append(c_complexity)
                data.append({'date': date,
                             'type': recommendation_type,
                             'topics': np.mean(calibration_topics),
                             'complexity': np.mean(calibration_complexity)})
        df = pd.DataFrame(data)
        self.visualize(df)
