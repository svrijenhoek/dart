import dart.metrics.affect
import dart.metrics.calibration
import dart.metrics.fragmentation
import dart.metrics.representation
import dart.metrics.alternative_voices
import dart.metrics.visualize
import pandas as pd
import numpy as np
import time
from random import sample

from datetime import datetime
from pathlib import Path


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

    def __init__(self, config, articles, recommendations, behavior_file):
        self.config = config

        self.recommendation_types = ['lstur', 'pop', 'random'] # self.handlers.recommendations.get_recommendation_types()
        self.Calibration = dart.metrics.calibration.Calibration(self.config)
        self.Fragmentation = dart.metrics.fragmentation.Fragmentation()
        self.Affect = dart.metrics.affect.Affect(self.config)
        self.Representation = dart.metrics.representation.Representation(self.config)
        self.AlternativeVoices = dart.metrics.alternative_voices.AlternativeVoices()

        self.articles = articles
        self.recommendations = recommendations
        self.behavior_file = behavior_file
        if self.config['test_size'] > 0:
            self.behavior_file = sample(self.behavior_file, self.config['test_size'])

        self.timer = {'calibration': 0, 'fragmentation': 0, 'affect': 0, 'representation': 0, 'alternative': 0,
                      'retrieving_articles': 0, 'sampling': 0}

    def create_sample(self):
        sample_impressions = np.random.choice(self.unique_impressions, size=5).tolist()
        return self.recommendations.loc[sample_impressions]

    def retrieve_articles(self, newsids):
        try:
            return self.articles.loc[newsids]
        except KeyError:
            return pd.DataFrame()

    def execute(self):
        success = 0
        failure = 0

        data = []
        print(str(datetime.now()) + "\tstarting calculations")
        start = time.time()
        all_entries = len(self.behavior_file)
        mod = round(all_entries/10)
        for i, impression in enumerate(self.behavior_file):
            tx = time.time()
            if i % mod == 0:
                print("{}/{}".format(i, all_entries))
            impr_index = impression['impression_index']
            hist = [article for article in impression['history']]
            hist.reverse()
            reading_history = self.retrieve_articles(hist)
            pool_articles = self.retrieve_articles(article for article in impression['items_without_click'])
            ty = time.time()
            sample = self.recommendations.sample(n=5)
            tz = time.time()
            self.timer['retrieving_articles'] += ty - tx
            self.timer['sampling'] += tz - ty
            recommendation = self.recommendations.loc[impr_index]
            for recommendation_type in self.recommendation_types:
                recommendation_articles = self.retrieve_articles([_id for _id in recommendation[recommendation_type]])
                if not recommendation_articles.empty and not pool_articles.empty:
                    t1 = time.time()
                    calibration = self.Calibration.calculate(reading_history, recommendation_articles)
                    t2 = time.time()
                    self.timer['calibration'] += t2-t1
                    # frag_sample = sample[sample[recommendation_type] == recommendation_type]
                    frag_articles = [self.retrieve_articles([_id for _id in articles])
                                     for articles in sample[recommendation_type]]
                    fragmentation = self.Fragmentation.calculate(frag_articles, recommendation_articles)
                    t3 = time.time()
                    self.timer['fragmentation'] += t3-t2
                    mean_affect, divergence_affect = self.Affect.calculate(pool_articles, recommendation_articles)
                    t4 = time.time()
                    self.timer['affect'] += t4-t3
                    representation = self.Representation.calculate(pool_articles, recommendation_articles)
                    t5 = time.time()
                    self.timer['representation'] += t5-t4
                    alternative_voices = self.AlternativeVoices.calculate(pool_articles, recommendation_articles)
                    t6 = time.time()
                    self.timer['alternative'] += t6-t5

                    row = {'impr_index': impr_index,
                        'rec_type': recommendation_type}
                    if calibration:
                        row['calibration_topic'] = calibration[0]
                        row['calibration_complexity'] = calibration[1]
                    if fragmentation: row['fragmentation'] = fragmentation
                    if divergence_affect: row['affect'] = divergence_affect
                    if representation: row['representation'] = representation
                    if alternative_voices:
                        row['alternative_voices'] = alternative_voices[2]
                        row['alternative_voices_ethnicity'] = alternative_voices[0]
                        row['alternative_voices_gender'] = alternative_voices[1]
                    if mean_affect: row['affect_mean'] = mean_affect
                    data.append(row)
                    success += 1
                else:
                    failure += 1

        print(self.timer)
        df = pd.DataFrame(data, columns=['impr_index', 'rec_type', 'calibration_topic', 'calibration_complexity', 'fragmentation',
                                         'affect', 'representation', 'alternative_voices', 'alternative_voices_ethnicity', 'alternative_voices_gender', 'affect_mean'])

        end = time.time()
        print(end - start)
        print(df.groupby('rec_type').mean().T)
        print(df.groupby('rec_type').std().T)

        print(str(success) +" successfully calculated")
        print(str(failure) + " failed")

        print(str(datetime.now()) + "\tdone")

        output_folder = self.config["output_folder"]
        self.write_to_file(df, output_folder)
        dart.metrics.visualize.Visualize.boxplot(df)
        dart.metrics.visualize.Visualize.violin_plot(df, output_folder)



    def write_to_file(self, df, output_folder):
        df.groupby('rec_type').mean().to_csv(Path(output_folder + 'summary.csv'), encoding='utf-8', mode='w')
        df.groupby('rec_type').std().to_csv(Path(output_folder + 'summary.csv'), encoding='utf-8', mode='a')
        df.to_csv(Path(output_folder + 'full.csv'), encoding='utf-8')



