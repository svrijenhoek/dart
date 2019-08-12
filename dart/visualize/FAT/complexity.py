from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt


class Readability:

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config

    def execute(self):
        data = []
        for date in self.config["recommendation_dates"]:
            upper = datetime.strptime(date, '%d-%m-%Y')
            lower = upper - timedelta(days=self.config["recommendation_range"])
            pool = self.handlers.articles.get_all_in_timerange(lower, upper)
            for recommendation_type in self.handlers.recommendations.get_recommendation_types():
                recommendations = self.handlers.recommendations.get_recommendations_at_date(date, recommendation_type)
                score = self.compare_complexity(recommendations, pool)
                data.append({'date': date, 'type': recommendation_type, 'score': score})
        df = pd.DataFrame(data)
        self.visualize(df)

    @staticmethod
    def visualize(df):
        plt.figure()
        df['date'] = pd.to_datetime(df['date'], format="%d-%m-%Y")
        df = df.sort_values('date', ascending=True)
        df.set_index('date', inplace=True)
        df.groupby('type')['score'].plot(legend=True)
        plt.draw()
        print(df.groupby('type')['score'].mean())

