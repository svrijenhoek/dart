import sys
import dart.visualize.FAT.personalization
import dart.visualize.FAT.coverage
import dart.visualize.FAT.politicalness
import dart.visualize.FAT.attention_distribution
import matplotlib.pyplot as plt

from datetime import datetime


class FATCalculator:
    """
    Class that calculates the metrics as identified for the FAT paper
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
        # print(str(datetime.now()) + "\t Politicalness")
        # dart.visualize.FAT.politicalness.Politicalness(self.handlers, self.config).execute()
        # print(str(datetime.now()) + "\t Coverage")
        # dart.visualize.FAT.coverage.Coverage(self.handlers, self.config).execute()
        # print(str(datetime.now()) + "\t Personalization")
        # dart.visualize.FAT.personalization.Personalization(self.handlers, self.config).execute()
        print(str(datetime.now()) + "\t Attention distribution")
        dart.visualize.FAT.attention_distribution.AttentionDistribution(self.handlers, self.config).execute()
        print(str(datetime.now()) + "\t Done")
        plt.show()


def main(argv):
    fc = FATCalculator()
    fc.execute()


if __name__ == "__main__":
    main(sys.argv[1:])

