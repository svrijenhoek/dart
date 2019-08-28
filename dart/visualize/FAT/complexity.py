from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class Complexity:

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config
        self.flesch_kincaid_map = {
            "Basisschool": [300, 70],
            "Onderbouw": [69, 60],
            "Bovenbouw": [59, 50],
            "Hoger onderwijs": [49, 30],
            "Universiteit": [29, -300]
        }

    def execute(self):
        data = []
        for date in self.config["recommendation_dates"]:
            upper = datetime.strptime(date, '%d-%m-%Y')
            lower = upper - timedelta(days=self.config["recommendation_range"])
            pool_complexities = [article.complexity for article in self.handlers.articles.get_all_in_timerange(lower, upper)]
            for recommendation_type in self.handlers.recommendations.get_recommendation_types():
                recommendations = self.handlers.recommendations.get_recommendations_at_date(date, recommendation_type)
                scores = []
                for recommendation in recommendations:
                    recommended_articles = self.handlers.articles.get_multiple_by_id(recommendation.articles)
                    recommended_complexities = [article.complexity for article in recommended_articles]
                    scores.append(self.compare_complexity(recommended_complexities, pool_complexities))
                data.append({'date': date, 'type': recommendation_type, 'score': np.mean(scores)})
        df = pd.DataFrame(data)
        self.visualize(df)

    def compare_complexity(self, recommendation, pool):
        r_mode = self.mode([self.discretize(complexity) for complexity in recommendation])
        if r_mode:
            r_index = list(self.flesch_kincaid_map).index(r_mode)
        p_mode = self.mode([self.discretize(complexity) for complexity in pool])
        if p_mode:
            p_index = list(self.flesch_kincaid_map).index(p_mode)
        try:
            return (p_index - r_index)/4
        except UnboundLocalError:
            return 0

    def discretize(self, value):
        for key in self.flesch_kincaid_map:
            complexity_range = self.flesch_kincaid_map[key]
            if complexity_range[1] < value < complexity_range[0]:
                return key

    @staticmethod
    def mode(lst):
        return max(set(lst), key=lst.count)

    @staticmethod
    def visualize(df):
        plt.figure()
        df['date'] = pd.to_datetime(df['date'], format="%d-%m-%Y")
        df = df.sort_values('date', ascending=True)
        df.set_index('date', inplace=True)
        df.groupby('type')['score'].plot(legend=True)
        plt.xticks(rotation='vertical')
        plt.draw()
        print(df.groupby('type')['score'].mean())

