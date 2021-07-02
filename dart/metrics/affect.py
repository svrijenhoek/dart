import math
import numpy as np
from sklearn.preprocessing import KBinsDiscretizer

class Affect:
    """
    Class that calculates the average Affect score based on absolute sentiment polarity values.
    This approach is an initial approximation of the concept, and should be refined in the future.
    Should also implement polarity analysis at index time.
    """

    def __init__(self, config):
        self.scores = {}
        self.language = config["language"]

    @staticmethod
    def harmonic_number(n):
        """Returns an approximate value of n-th harmonic number.

        http://en.wikipedia.org/wiki/Harmonic_number
        """
        # Euler-Mascheroni constant
        gamma = 0.57721566490153286060651209008240243104215933593992
        return gamma + math.log(n) + 0.5 / n - 1. / (12 * n ** 2) + 1. / (120 * n ** 4)

    def compute_polarity_distr(self, arr, bins_discretizer, adjusted=False):
        """ 
            Args:
            Return"
        """
        assert len(arr) > 0
        n = len(arr)
        sum_one_over_ranks = self.harmonic_number(n)
        arr_binned = bins_discretizer.transform(arr)
        distr = {}
        if adjusted:
            for bin in list(range(bins_discretizer.n_bins)):
                for indx, ele in enumerate(arr_binned[:,0]):
                    if ele == bin:
                        rank = indx + 1
                        bin_freq = distr.get(bin, 0.)
                        distr[bin] = bin_freq + 1 * 1 / rank / sum_one_over_ranks

        else:
            for bin in list(range(bins_discretizer.n_bins)):
                distr[bin] = round(np.count_nonzero(arr_binned == bin) / arr_binned.shape[0], 2) 
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

    def calculate(self, pool, recommendation):
        # pool_scores = np.mean([abs(article.sentiment) for article in pool])
        # recommendation_scores = np.mean([abs(article.sentiment) for article in recommendation])
        # diff = recommendation_scores - pool_scores
        n_bins = 5
        bins_discretizer = KBinsDiscretizer(encode='ordinal', n_bins=n_bins, strategy='quantile')
        arr_pool = np.array([abs(item.sentiment) for item in pool])
        bins_discretizer.fit(arr_pool)
        arr_recommendation = np.array([abs(item.sentiment) for item in recommendation])
        distr_pool  = self.compute_polarity_distr(self, arr_pool, bins_discretizer, adjusted=True)
        distr_recommendation = self.compute_polarity_distr(self, arr_recommendation, bins_discretizer, adjusted=True)
        divergence = self.compute_kl_divergence(distr_pool, distr_recommendation)
        return divergence
