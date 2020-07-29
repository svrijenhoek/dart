import sys
import dart.visualize.deprecated.personalization
import dart.visualize.deprecated.coverage
import dart.visualize.deprecated.politicalness
import dart.visualize.deprecated.attention_distribution
import dart.visualize.deprecated.defragmentation
import dart.visualize.deprecated.complexity
import matplotlib.pyplot as plt

from datetime import datetime


class FATCalculator:
    """
    Class that calculates the metrics as identified for the deprecated paper
    - Personalization
      - of style
      - of content
    - Politicalness
    - Impartiality
    - Minority voices (induction effect)
    - Defragmentation
    - Guidance towards expertise
    - Neutrality
    - Quality (?)
    """

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config

    def execute(self):
        print(str(datetime.now()) + "\t Personalization")
        dart.visualize.deprecated.personalization.Personalization(self.handlers, self.config).execute()
        print(str(datetime.now()) + "\t Politicalness")
        dart.visualize.deprecated.politicalness.Politicalness(self.handlers, self.config).execute()
        print(str(datetime.now()) + "\t Attention distribution")
        dart.visualize.deprecated.attention_distribution.AttentionDistribution(self.handlers, self.config).execute()
        print(str(datetime.now()) + "\t Complexity")
        dart.visualize.deprecated.complexity.Complexity(self.handlers, self.config).execute()
        print(str(datetime.now()) + "\t Defragmentation")
        dart.visualize.deprecated.defragmentation.Defragmentation(self.handlers, self.config).execute()
        print(str(datetime.now()) + "\t Coverage")
        dart.visualize.deprecated.coverage.Coverage(self.handlers, self.config).execute()
        print(str(datetime.now()) + "\t Done")
        plt.show()

