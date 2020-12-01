import numpy as np
import pandas as pd
import dart.visualize.visualize as visualize
import datetime


class Calibration:

    """
    Class that calibrates recommender Calibration.

    Theory: https://dl.acm.org/doi/10.1145/3240323.3240372
    Implementation: http://ethen8181.github.io/machine-learning/recsys/calibration/calibrated_reco.html.
    """

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config
        self.users = self.handlers.users.get_all_users()
        if self.config['test_size'] > 0:
            self.users = self.users[:self.config['test_size']:]

    def calculate_calibration(self, date, recommendation_type):
        calibration_topics = []
        calibration_complexity = []
        for user in self.users:
            recommendation = self.handlers.recommendations.get_recommendations_to_user_at_date(
                user.id,
                date,
                recommendation_type)
            if recommendation:
                reading_history = user.select_reading_history(date, recommendation_type)
                if reading_history:
                    recommendation_articles = self.handlers.articles.get_multiple_by_id(recommendation[0].articles)
                    reading_history_articles = self.handlers.articles.get_multiple_by_id(reading_history)
                    # calculate topics divergence
                    topics_divergence = self.calculate_categorical_divergence(
                        [article.editorialTags for article in recommendation_articles],
                        [article.editorialTags for article in reading_history_articles])
                    if topics_divergence:
                        calibration_topics.append(topics_divergence)
                    # calculate complexity divergence
                    complexity_divergence = self.calculate_numerical_divergence(
                        [article.complexity for article in recommendation_articles],
                        [article.complexity for article in reading_history_articles])
                    if complexity_divergence:
                        calibration_complexity.append(complexity_divergence)
        return calibration_topics, calibration_complexity

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
        to_remove = []
        for item, topic_freq in distr.items():
            normed_topic_freq = round(topic_freq / count, 2)
            if normed_topic_freq == 0:
                to_remove.append(item)
            else:
                distr[item] = normed_topic_freq

        for item in to_remove:
            del distr[item]

        return distr

    def calculate_categorical_divergence(self, l1, l2):
        freq_rec = self.compute_topic_distr(l1)
        freq_history = self.compute_topic_distr(l2)
        if freq_rec and freq_history:
            return self.compute_kl_divergence(freq_history, freq_rec)
        else:
            return

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

    @staticmethod
    def calculate_numerical_divergence(l1, l2):
        if l1 and l2:
            return abs(np.mean(l1) - np.mean(l2))
        else:
            return

    def execute(self):
        topic_data = []
        complexity_data = []
        no_dates = len(self.config["recommendation_dates"])
        marker =no_dates/10
        for x, date in enumerate(self.config["recommendation_dates"]):
            if x % marker < 1:
                print(str(datetime.datetime.now()) + "\t\t\t{:.0f}% completed".format(x/no_dates*100))
            for recommendation_type in self.handlers.recommendations.get_recommendation_types():
                topic_calibration_scores, complexity_calibration_scores = self.calculate_calibration(date, recommendation_type)
                if topic_calibration_scores:
                    topic_data.append({'date': date,
                                       'type': recommendation_type,
                                       'mean': np.mean(topic_calibration_scores),
                                       'std': np.std(topic_calibration_scores)})
                if complexity_calibration_scores:
                    complexity_data.append({'date': date,
                                            'type': recommendation_type,
                                            'mean': np.mean(complexity_calibration_scores),
                                            'std': np.std(complexity_calibration_scores)})
        df = pd.DataFrame(topic_data)
        self.visualize(df, "Calibration (topics)")
        df = pd.DataFrame(complexity_data)
        self.visualize(df, "Calibration (complexity)")

    @staticmethod
    def visualize(df, title):
        visualize.Visualize.print_mean(df)
        visualize.Visualize.plot(df, title)
