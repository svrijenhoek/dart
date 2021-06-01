import numpy as np


class Calibration:

    """
    Class that calibrates recommender Calibration.
    Theory: https://dl.acm.org/doi/10.1145/3240323.3240372
    Implementation: http://ethen8181.github.io/machine-learning/recsys/calibration/calibrated_reco.html.
    """

    def __init__(self):
        pass

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

    def calculate(self, reading_history, recommendation):
        return self.calculate_categorical_divergence(
            [article.source['subcategory'] for article in recommendation],
            [article.source['subcategory'] for article in reading_history])
