import sys
import dart.visualize.metrics.affect
import dart.visualize.metrics.calibration
import dart.visualize.metrics.fragmentation
import dart.visualize.metrics.representation
import dart.visualize.metrics.inclusion
import matplotlib.pyplot as plt

from datetime import datetime


class MetricsCalculator:
    """
    Class that calculates the metrics as identified for the new FAT paper
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
        print(str(datetime.now()) + "\t Calibration")
        dart.visualize.metrics.calibration.Calibration(self.handlers, self.config).execute()
        print(str(datetime.now()) + "\t Fragmentation")
        dart.visualize.metrics.fragmentation.Fragmentation(self.handlers, self.config).execute()
        print(str(datetime.now()) + "\t Affect")
        dart.visualize.metrics.affect.Affect(self.handlers, self.config).execute()
        print(str(datetime.now()) + "\t Representation")
        dart.visualize.metrics.representation.Representation(self.handlers, self.config).execute()
        print(str(datetime.now()) + "\t Inclusion")
        dart.visualize.metrics.inclusion.Inclusion(self.handlers, self.config).execute()
        print(str(datetime.now()) + "\t Done")
        plt.show()

