import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


class Coverage:

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config

        self.story_percentage_threshold = 0.0
        self.user_percentage_threshold = 0.0
        self.timerange = config["recommendation_range"]

    def is_covered(self, story, recommendations):
        number_of_articles_in_story = len(story.docids)
        users_have_seen_story = 0
        for recommendation in recommendations:
            articles_seen = []
            for docid in recommendation.articles:
                if docid in story.docids:
                    articles_seen.append(docid)
            if len(articles_seen)/number_of_articles_in_story > self.story_percentage_threshold:
                users_have_seen_story += 1
        return users_have_seen_story/len(recommendations) > self.user_percentage_threshold

    def calculate_coverage(self, stories, recommendations):
        count = 0
        for story in stories:
            if len(story.docids) > 1:
                if self.is_covered(story, recommendations):
                    count += 1
        return count/len(stories)

    @staticmethod
    def visualize(df):
        df['date'] = pd.to_datetime(df['date'], format="%d-%m-%Y")
        df = df.sort_values('date', ascending=True)
        df.set_index('date', inplace=True)
        plt.figure()
        df.groupby('type')['coverage'].plot(legend=True)
        plt.xticks(rotation='vertical')
        plt.draw()
        print(df.groupby('type')['coverage'].mean())

    def execute(self):
        """
        Calculates the percentage of stories that have been presented to at least x percent of users
        """
        print("===COVERAGE===")
        data = []
        for date in self.config['recommendation_dates']:
            upper = datetime.strptime(date, '%d-%m-%Y')
            lower = upper - timedelta(days=self.timerange)
            stories = self.handlers.stories.get_stories_at_date(upper, lower)
            for recommendation_type in self.handlers.recommendations.get_recommendation_types():
                recommendations = self.handlers.recommendations.get_recommendations_at_date(date, recommendation_type)
                if recommendations and stories:
                    coverage = self.calculate_coverage(stories, recommendations)
                    data.append({'date': date, 'type': recommendation_type, 'coverage': coverage})
        df = pd.DataFrame(data)
        self.visualize(df)
