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

    def compute_polarity_distr(self, arr, bins_discretizer):
        """ 
            Args:
            Return"
        """
        assert len(pool) > 0
        arr_binned = bins_discretizer.transform(arr)
        distr = {}
        for bin in list(range(enc.n_bins)):
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
        distr_pool  = self.compute_polarity_distr(self, arr_pool, bins_discretizer)
        distr_recommendation = self.compute_polarity_distr(self, arr_recommendation, bins_discretizer)
        divergence = self.compute_kl_divergence(distr_pool, distr_recommendation)
        return divergence
