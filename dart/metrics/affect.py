import numpy as np
from sklearn.preprocessing import KBinsDiscretizer
from dart.external.kl_divergence import compute_kl_divergence
from dart.external.discount import harmonic_number


class Affect:
    """
    Class that calculates the average Affect score based on absolute sentiment polarity values.
    This approach is an initial approximation of the concept, and should be refined in the future.
    Should also implement polarity analysis at index time.
    """

    def __init__(self, config):
        n_bins = 5
        self.bins_discretizer = KBinsDiscretizer(encode='ordinal', n_bins=n_bins, strategy='quantile')

    def compute_distr(self, arr, bins_discretizer, adjusted=False):
        """
            Args:
            Return"
        """
        assert len(arr) > 0
        n = len(arr)
        sum_one_over_ranks = harmonic_number(n)
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

    def calculate(self, pool, recommendation):
        arr_pool = np.array([abs(item.sentiment) for item in pool]).reshape(-1, 1)
        arr_recommendation = np.array([abs(item.sentiment) for item in recommendation]).reshape(-1, 1)

        self.bins_discretizer.fit(arr_pool)
        distr_pool = self.compute_distr(arr_pool, self.bins_discretizer)
        distr_recommendation = self.compute_distr(arr_recommendation, self.bins_discretizer)
        return compute_kl_divergence(distr_pool, distr_recommendation)
