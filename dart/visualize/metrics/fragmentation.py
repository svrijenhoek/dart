import numpy as np
from dart.external.rbo import rbo


class Fragmentation:
    """
    Class that calculates to what extent users have seen the same news stories.
    A "story" is considered a set of articles that are about the same 'event'.

    Calculation is based on the Rank Biased Overlap specified in http://codalism.com/research/papers/wmz10_tois.pdf
    Implementation from https://github.com/dlukes/rbo/blob/master/rbo.py
    """

    def __init__(self):
        pass

    def calculate(self, sample, recommendation):
        fragmentations = []
        stories_x = [article.story for article in recommendation]
        for y in sample:
            stories_y = [article.story for article in y]
            fragmentations.append(self.compare_recommendations(stories_x, stories_y))
        return np.mean(fragmentations)

    @staticmethod
    def compare_recommendations(x, y):
        if x and y:
            output = rbo(x, y, 0.9)
            return output.ext
        else:
            return 0
