import dart.visualize.metrics.affect
import dart.visualize.metrics.calibration
import dart.visualize.metrics.fragmentation
import dart.visualize.metrics.representation
import dart.visualize.metrics.alternative_voices
import pandas as pd

from datetime import datetime
import random
import dart.Util as Util


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

        self.recommendation_types = self.handlers.recommendations.get_recommendation_types()
        self.Calibration = dart.visualize.metrics.calibration.Calibration()
        self.Fragmentation = dart.visualize.metrics.fragmentation.Fragmentation()
        self.Affect = dart.visualize.metrics.affect.Affect(self.config)
        self.Representation = dart.visualize.metrics.representation.Representation(self.config)
        self.AlternativeVoices = dart.visualize.metrics.alternative_voices.AlternativeVoices()

    def create_sample(self, behavior_file):
        sample = []
        slice = random.sample(behavior_file, 20)
        for entry in slice:
            line = {}
            for recommendation_type in self.recommendation_types:
                recommendation = self.handlers.recommendations.get_recommendation_with_index_and_type(entry['impression_index'], recommendation_type)
                articles = self.handlers.articles.get_multiple_by_id(recommendation.articles)
                line[recommendation_type] = articles
            sample.append(line)
        return sample

    def execute(self):
        behavior_file = Util.read_behavior_file(self.config['behavior_file'])
        data = []
        for impression in behavior_file[1:self.config['test_size']]:
            impr_index = impression['impression_index']
            reading_history = self.handlers.articles.get_multiple_by_newsid(impression['history'])
            pool = self.handlers.articles.get_multiple_by_newsid(impression['items_without_click'])
            sample = self.create_sample(behavior_file)
            for recommendation_type in self.recommendation_types:
                recommendation = self.handlers.recommendations.get_recommendation_with_index_and_type(impr_index, recommendation_type)
                recommendation_articles = self.handlers.articles.get_multiple_by_id(recommendation.articles)
                calibration = self.Calibration.calculate(reading_history, recommendation_articles)
                frag_sample = [entry[recommendation_type] for entry in sample]
                fragmentation = self.Fragmentation.calculate(frag_sample, recommendation_articles)
                affect = self.Affect.calculate(pool, recommendation_articles)
                representation = self.Representation.calculate(pool, recommendation_articles)
                alternative_voices = self.AlternativeVoices.calculate(pool, recommendation_articles)
                data.append({'impr_index': impr_index, 'rec_type': recommendation_type,
                           'calibration': calibration, 'fragmentation': fragmentation,
                           'affect': affect, 'representation': representation, 'alternative_ethnicity': alternative_voices[0], 'alternative_gender': alternative_voices[1]})
        df = pd.DataFrame(data)
        print(df.groupby('rec_type').mean())
        print(df.groupby('rec_type').std())
        # print(df)


