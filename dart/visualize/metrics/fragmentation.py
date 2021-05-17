import pandas as pd
import numpy as np
import dart.visualize.visualize as visualize
import datetime

from collections import Counter
from dart.external.rbo import rbo


class Fragmentation:

    """
    Class that calculates to what extent users have seen the same news stories.
    A "story" is considered a set of articles that are about the same 'event'.

    Calculation is based on the Rank Biased Overlap specified in http://codalism.com/research/papers/wmz10_tois.pdf
    Implementation from https://github.com/dlukes/rbo/blob/master/rbo.py
    """

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config

        self.stories = {}
        self.article_to_story = {}
        self.unknown_articles = Counter()

    def execute(self):
        data = []
        no_dates = len(self.config["recommendation_dates"])
        marker = no_dates/10
        for x, date in enumerate(self.config["recommendation_dates"]):
            if x % marker < 1:
                print(str(datetime.datetime.now()) + "\t\t\t{:.0f}% completed".format(x/no_dates*100))
            for recommendation_type in self.handlers.recommendations.get_recommendation_types():
                fragmentations = []
                recommendations = self.handlers.recommendations.get_recommendations_at_date(date, recommendation_type)
                if recommendations:
                    if self.config['test_size'] > 0:
                        recommendations = recommendations[1:self.config['test_size']]
                    for ix, x in enumerate(recommendations):
                        stories_x = self.get_stories(x)
                        for iy, y in enumerate(recommendations):
                            if iy > ix:
                                stories_y = self.get_stories(y)
                                fragmentations.append(self.compare_recommendations(stories_x, stories_y))
                    data.append({'date': date, 'type': recommendation_type,
                                 'mean': np.mean(fragmentations), 'std': np.std(fragmentations)})
        df = pd.DataFrame(data)
        self.visualize(df)

    def get_stories(self, recommendation):
        """
        Retrieve all story ids for each article in the recommendation
        """
        if recommendation.id not in self.stories:
            articles = []
            for docid in recommendation.articles:
                if docid not in self.article_to_story:
                    try:
                        story = self.handlers.stories.get_story_with_id(docid)
                        self.article_to_story[docid] = story.identifier
                        articles.append(self.article_to_story[docid])
                    except AttributeError:
                        self.unknown_articles[docid] += 1
            self.stories[recommendation.id] = articles
        return self.stories[recommendation.id]

    @staticmethod
    def compare_recommendations(x, y):
        if x and y:
            output = rbo(x, y, 0.9)
            return output.ext
        else:
            return 0

    @staticmethod
    def visualize(df):
        visualize.Visualize.print_mean(df)
        visualize.Visualize.plot(df, "Fragmentation")
