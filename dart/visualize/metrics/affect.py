import numpy as np


class Affect:
    """
    Class that calculates the average Affect score based on absolute sentiment polarity values.
    This approach is an initial approximation of the concept, and should be refined in the future.
    Should also implement polarity analysis at index time.
    """

    def __init__(self, config):
        self.scores = {}
        self.language = config["language"]

    def calculate(self, pool, recommendation):
        pool_scores = np.mean([abs(article.sentiment) for article in pool])
        recommendation_scores = np.mean([abs(article.sentiment) for article in recommendation])
        diff = recommendation_scores - pool_scores
        return diff
