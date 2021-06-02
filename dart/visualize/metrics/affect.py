from textblob import TextBlob
from textblob_de import TextBlobDE
from textblob_nl import PatternTagger, PatternAnalyzer
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

    def analyze(self, text):
        # Analyze the polarity of each text in the appropriate language.
        # Uses Textblob mainly because of its ease of implementation in multiple languages.
        # Dutch Textblob uses the same engine as the English one, but with special Pattern tagger and analyzer.
        if self.language == 'dutch':
            blob = TextBlob(text, pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())
        elif self.language == 'english':
            blob = TextBlob(text)
        elif self.language == 'german':
            blob = TextBlobDE(text)
        return blob

    def get_affect_score(self, article):
        # If we calculated the polarity
        if article.id not in self.scores:
            # use sentiment analysis to retrieve a polarity score
            blob = self.analyze(article.text)
            polarity = blob.polarity
            self.scores[article.id] = abs(polarity)
        return self.scores[article.id]

    def calculate(self, pool, recommendation):
        pool_scores = np.mean([self.get_affect_score(article) for article in pool])
        recommendation_scores = np.mean([self.get_affect_score(article) for article in recommendation])
        diff = recommendation_scores - pool_scores
        return diff
