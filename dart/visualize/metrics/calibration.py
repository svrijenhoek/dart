import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math


class Calibration:

    """
    Class that calibrates recommender Calibration.

    Theory: https://dl.acm.org/doi/10.1145/3240323.3240372
    Implementation: http://ethen8181.github.io/machine-learning/recsys/calibration/calibrated_reco.html.
    """

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
    def compute_topic_distr(items):
        """Compute the topic distribution for a given list of Items."""
        count = 0
        distr = {}
        for item in items:
            if not item == 'unavailable':
                for topic in item:
                    topic_freq = distr.get(topic, 0.)
                    distr[topic] = topic_freq + 1
                    count += 1

        # we normalize the summed up probability so it sums up to 1
        # and round it to three decimal places, adding more precision
        # doesn't add much value and clutters the output
        for item, topic_freq in distr.items():
            normed_topic_freq = round(topic_freq / count, 4)
            distr[item] = normed_topic_freq

        return distr

    @staticmethod
    def compute_kl_divergence(interacted_distr, reco_distr, alpha=0.01):
        """
        KL (p || q), the lower the better.
        alpha is not really a tuning parameter, it's just there to make the
        computation more numerically stable.
        """
        kl_div = 0.
        for genre, score in interacted_distr.items():
            try:
                reco_score = reco_distr.get(genre, 0.)
                reco_score = (1 - alpha) * reco_score + alpha * score
                kl_div += score * np.log2(score / reco_score)
            except ZeroDivisionError:
                print(interacted_distr)
                print(reco_distr)

        return kl_div

    def calculate_categorical_divergence(self, l1, l2):
        freq_rec = self.compute_topic_distr(l1)
        freq_history = self.compute_topic_distr(l2)
        if freq_rec and freq_history:
            return self.compute_kl_divergence(freq_history, freq_rec)
        else:
            return

    @staticmethod
    def calculate_numerical_divergence(l1, l2):
        if l1 and l2:
            return abs(np.mean(l1) - np.mean(l2))
        else:
            return

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
                        if reading_history:
                            c_topics, c_complexity = self.calculate_calibration(recommendation[0].articles, reading_history)
                            if c_topics:
                                calibration_topics.append(c_topics)
                            if c_complexity:
                                calibration_complexity.append(c_complexity)
                data.append({'date': date,
                             'type': recommendation_type,
                             'topics': np.mean(calibration_topics),
                             'complexity': np.mean(calibration_complexity)})
        df = pd.DataFrame(data)
        self.visualize(df)
