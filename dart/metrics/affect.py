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

    def calculate(self, pool, recommendation):
        # pool_scores = np.mean([abs(article.sentiment) for article in pool])
        # recommendation_scores = np.mean([abs(article.sentiment) for article in recommendation])
        # diff = recommendation_scores - pool_scores
        n_bins = 5
        bins_discretizer = KBinsDiscretizer(encode='ordinal', n_bins=n_bins, strategy='quantile')
        arr_pool = np.array([abs(item.sentiment) for item in pool])
        bins_discretizer.fit(arr_pool)
        arr_recommendation = np.array([abs(item.sentiment) for item in recommendation])
        distr_pool  = compute_polarity_distr(self, arr_pool, bins_discretizer)
        distr_recommendation = compute_polarity_distr(self, arr_recommendation, bins_discretizer)
        # TODO: calc the KL (distr_pool || distr_recommendation)
        return diff
