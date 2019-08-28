import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class Defragmentation:

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config

        self.stories = {}
        self.article_to_story = {}

    def execute(self):
        data = []
        for date in self.config["recommendation_dates"]:
            for recommendation_type in self.handlers.recommendations.get_recommendation_types():
                defragmentations = []
                recommendations = self.handlers.recommendations.get_recommendations_at_date(date, recommendation_type)
                for ix, x in enumerate(recommendations):
                    stories_x = self.get_stories(x)
                    for iy, y in enumerate(recommendations):
                        if iy > ix:
                            stories_y = self.get_stories(y)
                            defragmentations.append(self.compare_recommendations(stories_x, stories_y))
                data.append({'date': date, 'type': recommendation_type, 'defragmentation': np.mean(defragmentations)})
        df = pd.DataFrame(data)
        self.visualize(df)

    def get_stories(self, recommendation):
        if recommendation.id not in self.stories:
            articles = []
            for docid in recommendation.articles:
                if docid not in self.article_to_story:
                    self.article_to_story[docid] = self.handlers.stories.get_story_with_id(docid).identifier
                articles.append(self.article_to_story[docid])
            self.stories[recommendation.id] = articles
        return self.stories[recommendation.id]

    @staticmethod
    def compare_recommendations(x, y):
        intersection = list(set(x) & set(y))
        union = list(set(x).union(y))
        return len(intersection)/len(union)

    @staticmethod
    def visualize(df):
        plt.figure()
        df['date'] = pd.to_datetime(df['date'], format="%d-%m-%Y")
        df = df.sort_values('date', ascending=True)
        df.set_index('date', inplace=True)
        df.groupby('type')['defragmentation'].plot(legend=True)
        plt.xticks(rotation='vertical')
        plt.draw()
        print(df.groupby('type')['defragmentation'].mean())
