import numpy as np
from dart.external.discount import harmonic_number
from dart.external.kl_divergence import compute_kl_divergence



class Fragmentation:
    """
    Class that calculates to what extent users have seen the same news stories.
    A "story" is considered a set of articles that are about the same 'event'.
    """

    def __init__(self):
        pass

    def compute_distr(self, items, adjusted=False):
        """Compute the genre distribution for a given list of Items."""
        n = len(items)
        sum_one_over_ranks = harmonic_number(n)
        count = 0
        distr = {}
        for indx, item in enumerate(items):
            rank = indx + 1
            for topic in list(item.source['story'].split(" ")):
                if not topic == 'unavailable':
                    topic_freq = distr.get(topic, 0.)
                    distr[topic] = topic_freq + 1 * 1 / rank / sum_one_over_ranks if adjusted else topic_freq + 1
                    count += 1

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

    def calculate(self, sample, recommendation):
        fragmentations = []
        stories_x = [article.story for article in recommendation]
        for y in sample:
            fragmentations.append(self.compare_recommendations(stories_x, y))
        return np.mean(fragmentations)

    def compare_recommendations(self, x, y):
        if x and y:
            # output = rbo(x, y, 0.9)
            freq_x = self.compute_distr(x, adjusted=True)
            freq_y = self.compute_distr(y, adjusted=True)
            divergence = 1/2*(compute_kl_divergence(freq_x, freq_y) + compute_kl_divergence(freq_y, freq_x))
            return divergence
        else:
            return 0
