import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from collections import Counter


class Defragmentation:

    """
    Class that calculates to what extent users have seen the same news stories.
    A "story" is considered a set of articles that are about the same 'event'.
    """

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config

        self.stories = {}
        self.article_to_story = {}
        self.unknown_articles = Counter()

    def execute(self):
        data = []
        for date in self.config["recommendation_dates"]:
            print(date)
            for recommendation_type in self.handlers.recommendations.get_recommendation_types():
                defragmentations = []
                recommendations = self.handlers.recommendations.get_recommendations_at_date(date, recommendation_type)
                if recommendations:
                    for ix, x in enumerate(recommendations):
                        stories_x = self.get_stories(x)
                        for iy, y in enumerate(recommendations):
                            if iy > ix:
                                stories_y = self.get_stories(y)
                                defragmentations.append(self.compare_recommendations(stories_x, stories_y))
                    data.append({'date': date, 'type': recommendation_type, 'defragmentation': np.mean(defragmentations)})
        df = pd.DataFrame(data)
        self.visualize(df, self.unknown_articles)

    def get_stories(self, recommendation):
        """
        Retrieve all story ids for each article in the recommendation
        """
        if recommendation.id not in self.stories:
            articles = []
            for docid in recommendation.articles:
                if docid not in self.article_to_story:
                    try:
                        self.article_to_story[docid] = self.handlers.stories.get_story_with_id(docid).identifier
                        articles.append(self.article_to_story[docid])
                    except AttributeError:
                        self.unknown_articles[docid] += 1
            self.stories[recommendation.id] = articles
        return self.stories[recommendation.id]

    @staticmethod
    def compare_recommendations(x, y):
        intersection = list(set(x) & set(y))
        union = list(set(x).union(y))
        if len(union) == 0:
            return 0
        return len(intersection)/len(union)

    @staticmethod
    def visualize(df, unknown_articles):
        print(unknown_articles)
        plt.figure()
        df['date'] = pd.to_datetime(df['date'], format="%d-%m-%Y")
        df = df.sort_values('date', ascending=True)
        df.set_index('date', inplace=True)
        df.groupby('type')['defragmentation'].plot(legend=True)
        plt.xticks(rotation='vertical')
        plt.draw()
        print(df.groupby('type')['defragmentation'].mean())
