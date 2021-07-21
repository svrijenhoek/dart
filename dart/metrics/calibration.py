from dart.external.discount import harmonic_number
from dart.external.kl_divergence import compute_kl_divergence


class Calibration:
    """
    Class that calibrates recommender Calibration.
    Theory: https://dl.acm.org/doi/10.1145/3240323.3240372
    Implementation: http://ethen8181.github.io/machine-learning/recsys/calibration/calibrated_reco.html.
    """

    def __init__(self, config):
        self.discount = config['discount']

    def compute_distr(self, items, adjusted=False):
        """Compute the genre distribution for a given list of Items."""
        n = len(items)
        sum_one_over_ranks = harmonic_number(n)
        count = 0
        distr = {}
        for _, item in items.iterrows():
            count += 1
            topic_freq = distr.get(item.subcategory, 0.)
            distr[item.subcategory] = topic_freq + 1 * 1 / count / sum_one_over_ranks if adjusted else topic_freq + 1

        # we normalize the summed up probability so it sums up to 1
        # and round it to three decimal places, adding more precision
        # doesn't add much value and clutters the output
        to_remove = []
        for topic, topic_freq in distr.items():
            normed_topic_freq = round(topic_freq / count, 2)
            if normed_topic_freq == 0:
                to_remove.append(topic)
            else:
                distr[topic] = normed_topic_freq

        for topic in to_remove:
            del distr[topic]

        return distr

    def calculate(self, reading_history, recommendation):
        if not reading_history.empty:
            freq_rec = self.compute_distr(recommendation, adjusted=False)
            freq_history = self.compute_distr(reading_history, adjusted=False)
            divergence = compute_kl_divergence(freq_history, freq_rec)
            return divergence
        else:
            return
