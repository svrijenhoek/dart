from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt


class Politicalness:

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config

    def execute(self):
        df = self.calculate()
        self.visualize(df)

    def calculate(self):
        data = []
        for date in self.config['recommendation_dates']:
            upper = datetime.strptime(date, '%d-%m-%Y')
            lower = upper - timedelta(days=self.config["recommendation_range"])
            pool = self.handlers.articles.get_all_in_timerange(lower, upper)
            pool_percentage = self.get_political_percentage(pool)
            for recommendation_type in self.handlers.recommendations.get_recommendation_types():
                recommendations = self.handlers.recommendations.get_recommendations_at_date(date, recommendation_type)
                percentages = self.get_average_percentage(recommendations)
                for percentage in percentages:
                    data.append({'date': date, 'type': recommendation_type, 'comparison': percentage-pool_percentage})
        df = pd.DataFrame(data)
        return df

    def get_average_percentage(self, recommendations):
        percentages = []
        for recommendation in recommendations:
            articles = self.handlers.articles.get_multiple_by_id(recommendation.articles)
            percentage = self.get_political_percentage(articles)
            percentages.append(percentage)
        return percentages

    def get_political_percentage(self, articles):
            classifications = [article.classification for article in articles]
            return classifications.count('politiek')/len(classifications)

    @staticmethod
    def visualize(df):
        print("===POLITICALNESS===")
        print(df.groupby('type')['comparison'].mean())
        # prepare dataframe for visualization
        df['date'] = pd.to_datetime(df['date'], format="%d-%m-%Y")
        df = df.sort_values('date', ascending=True)
        unique_types = df.type.unique()
        fig, axes = plt.subplots(ncols=len(unique_types), sharey=True, figsize=(9, 3))
        # iterate over different types of recommendations
        for i, recommendation_type in enumerate(unique_types):
            ax = axes[i]
            ax.set_title(recommendation_type)
            df1 = df[df['type'] == recommendation_type]
            df_mean = df1.groupby(df1.date)['comparison'].mean()
            # create plots
            ax.scatter(x='date', y='comparison', data=df1)
            ax.plot(df_mean, '*-y')
        plt.xticks(rotation='vertical')
        plt.draw()
