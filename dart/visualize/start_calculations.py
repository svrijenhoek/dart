import dart.visualize.metrics.affect
import dart.visualize.metrics.calibration
import dart.visualize.metrics.fragmentation
import dart.visualize.metrics.representation
import dart.visualize.metrics.alternative_voices
import matplotlib.pyplot as plt

from datetime import datetime


class MetricsCalculator:
    """
    Class that calculates the metrics as identified for the new deprecated paper
    - Calibration
      - of style
      - of content
    - Fragmentation
    - Affect
    - Representation
    - Inclusion
    """

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config

    def execute(self):
        if "calibration" in self.config["metrics"]:
            print(str(datetime.now()) + "\t Calibration")
            dart.visualize.metrics.calibration.Calibration(self.handlers, self.config).execute()
        if "fragmentation" in self.config["metrics"]:
            print(str(datetime.now()) + "\t Fragmentation")
            dart.visualize.metrics.fragmentation.Fragmentation(self.handlers, self.config).execute()
        if "affect" in self.config["metrics"]:
           print(str(datetime.now()) + "\t Affect")
           dart.visualize.metrics.affect.Affect(self.handlers, self.config).execute()
        if "representation" in self.config["metrics"]:
            print(str(datetime.now()) + "\t Representation")
            dart.visualize.metrics.representation.Representation(self.handlers, self.config).execute_mind()
        if "inclusion" in self.config["metrics"]:
            print(str(datetime.now()) + "\t Alternative Voices")
            dart.visualize.metrics.alternative_voices.AlternativeVoices(self.handlers, self.config).execute()
        print(str(datetime.now()) + "\t Done")
        # Create legend & Show graphic
        plt.legend()
        plt.show()

