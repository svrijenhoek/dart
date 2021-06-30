import metrics.affect
import metrics.calibration
import metrics.fragmentation
import metrics.representation
import metrics.alternative_voices
import pandas as pd
import time

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

        self.recommendation_types = ['lstur', 'naml', 'random'] # self.handlers.recommendations.get_recommendation_types()
        self.Calibration = metrics.calibration.Calibration(self.config)
        self.Fragmentation = metrics.fragmentation.Fragmentation()
        self.Affect = metrics.affect.Affect(self.config)
        self.Representation = metrics.representation.Representation(self.config)
        self.AlternativeVoices = metrics.alternative_voices.AlternativeVoices()

        self.behavior_file = Util.read_behavior_file(self.config['behavior_file'])
        if self.config['test_size'] > 0:
            self.behavior_file = self.behavior_file[:self.config['test_size']]
        self.articles = self.handlers.articles.get_all_articles_in_dict()
        self.mapping = self.news_id_to_id()

        self.stories = {key: [] for key in self.recommendation_types}

    def create_sample(self):
        sample = []
        random_selection = [random.randrange(len(self.stories[self.recommendation_types[0]]))
                            for _ in range(min(len(self.stories[self.recommendation_types[0]]), 100))]
        for entry in random_selection:
            line = {}
            for recommendation_type in self.recommendation_types:
                line[recommendation_type] = self.stories[recommendation_type][entry]
            sample.append(line)
        return sample

    def news_id_to_id(self):
        mapping = {}
        for _id, article in self.articles.items():
            mapping[article.source['newsid']] = _id
        return mapping

    def execute(self):
        data = []
        print(str(datetime.now()) + "\tstarting calculations")
        start = time.time()
        for impression in self.behavior_file:
            impr_index = impression['impression_index']
            try:
                reading_history = [self.articles[self.mapping[article]] for article in impression['history']
                                   if article in self.mapping]
                reading_history.reverse()
            except KeyError:
                reading_history = []
            pool = [self.articles[self.mapping[article]] for article in impression['items_without_click']
                    if article in self.mapping]
            sample = self.create_sample()

            for recommendation_type in self.recommendation_types:
                recommendation = self.handlers.recommendations.get_recommendation_with_index_and_type(impr_index, recommendation_type)
                recommendation_articles = [self.articles[_id] for _id in recommendation.articles]

                calibration = self.Calibration.calculate(reading_history, recommendation_articles)
                frag_sample = [entry[recommendation_type] for entry in sample]
                fragmentation = self.Fragmentation.calculate(frag_sample, recommendation_articles)
                affect = self.Affect.calculate(pool, recommendation_articles)
                representation = self.Representation.calculate(pool, recommendation_articles)
                alternative_voices = self.AlternativeVoices.calculate(pool, recommendation_articles)

                data.append({'impr_index': impr_index, 'rec_type': recommendation_type,
                          'calibration': calibration, 'fragmentation': fragmentation,
                          'affect': affect, 'representation': representation, 'alternative_ethnicity': alternative_voices[0], 'alternative_gender': alternative_voices[1]})
                self.stories[recommendation_type].append([article.story for article in recommendation_articles])

        df = pd.DataFrame(data)
        self.write_to_file(df)

        end = time.time()
        print(end - start)
        print(df.groupby('rec_type').mean())
        print(df.groupby('rec_type').std())
        print(str(datetime.now()) + "\tdone")

    def write_to_file(self, df):
        output_filename = 'output/'\
                          + datetime.now().strftime("%Y-%m-%d") \
                          + '_' + str(self.config['test_size'])
        df.groupby('rec_type').mean().to_csv(output_filename + '_summary.csv', encoding='utf-8', mode='w')
        df.groupby('rec_type').std().to_csv(output_filename + '_summary.csv', encoding='utf-8', mode='a')
        df.to_csv(output_filename + '_full.csv', encoding='utf-8')



