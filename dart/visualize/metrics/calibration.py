import math
import numpy as np
from scipy.stats import entropy
from scipy.special import rel_entr


class Calibration:
    """
    Class that calibrates recommender Calibration.
    Theory: https://dl.acm.org/doi/10.1145/3240323.3240372
    Implementation: http://ethen8181.github.io/machine-learning/recsys/calibration/calibrated_reco.html.
    """

    def __init__(self):
        pass


    @staticmethod
    def harmonic_number(n):
        """Returns an approximate value of n-th harmonic number.

        http://en.wikipedia.org/wiki/Harmonic_number
        """
        # Euler-Mascheroni constant
        gamma = 0.57721566490153286060651209008240243104215933593992
        return gamma + math.log(n) + 0.5/n - 1./(12*n**2) + 1./(120*n**4)

    
    @staticmethod
    def compute_topic_distr(items, adjusted=False):
        """Compute the topic distribution for a given list of Items.
            Params:
                items: a list of item indexes (the 1st item is the most 'relevant' or with higher rank)
        """
        count = 0
        distr = {}
        n = len(items)
        sum_one_over_ranks = harmonic_number(n)
        for indx, topic in enumerate(items):
            rank = indx + 1
            if not topic == 'unavailable':
                topic_freq = distr.get(topic, 0.)
                if adjusted:
                    distr[topic] = ((topic_freq + 1)/rank)/sum_one_over_ranks
                else:
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
        freq_rec = self.compute_topic_distr(l1.reverse(), adjusted=True)
        freq_history = self.compute_topic_distr(l2.reverse(), adjusted=True)
        # for item in freq_history:
        #     if item not in freq_rec:
        #         freq_rec[item] = 0
        # for item in freq_rec:
        #     if item not in freq_history:
        #         freq_history[item] = 0
        # sorted_freq = [v for k, v in dict(sorted(freq_rec.items())).items()]
        # sorted_hist = [v for k, v in dict(sorted(freq_history.items())).items()]
        # vec = rel_entr(sorted_freq, sorted_hist)
        # vec = np.ma.masked_invalid(vec).compressed()
        divergence = self.compute_kl_divergence(freq_history, freq_rec)
        return divergence
    
    def calculate(self, reading_history, recommendation):
        return self.calculate_categorical_divergence(
            [article.source['category'] for article in recommendation],
            [article.source['category'] for article in reading_history])
