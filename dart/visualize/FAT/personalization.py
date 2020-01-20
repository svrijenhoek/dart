from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import dart.handler.NLP.cosine_similarity


class Personalization:

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
        df = self.calculate_personalization()
        self.visualize_content(df)
        self.visualize_style(df)

    def discretize(self, value):
        for key in self.flesch_kincaid_map:
            complexity_range = self.flesch_kincaid_map[key]
            if complexity_range[1] < value < complexity_range[0]:
                return key

    @staticmethod
    def mode(lst):
        try:
            return max(set(lst), key=lst.count)
        except ValueError:
            return None

    def calculate_personalization(self):
        """
        Method that calculates the internal cosine similarity between the current recommendation and all documents in
        the reading history
        """
        cos = dart.handler.NLP.cosine_similarity.CosineSimilarity(self.config['language'])
        recommendation_types = self.handlers.recommendations.get_recommendation_types()
        data = []
        users = self.handlers.users.get_all_users()
        too_short = 0
        for user in users:
            gen = (rec for rec in recommendation_types if rec in user.reading_history)
            for recommendation_type in gen:
                try:
                    dates = user.reading_history[recommendation_type].keys()
                    strp_dates = [datetime.strptime(date, '%d-%m-%Y') for date in dates]
                    last_date = min(strp_dates)
                    reading_history = user.select_reading_history(last_date, recommendation_type)
                    if len(reading_history) > 1:
                        cosine_mean, cosine_std = cos.calculate_all(reading_history)
                        # cosine = cos.calculate_cosine_experiment(recommended_ids, reading_history)
                        mean_distance, std_distance = self.calculate_all_distances(reading_history)
                        data.append({"user": user.id, "type": recommendation_type, "cosine_mean": cosine_mean, "cosine_std": cosine_std,
                                     "distance_mean": mean_distance, "distance_std": std_distance})
                    else:
                        too_short += 1
                except ValueError:
                    too_short += 1
        df = pd.DataFrame(data, columns=["user", "type", "cosine_mean", "cosine_std", "distance_mean", "distance_std"])
        print("Number of users with too short reading history: {}".format(too_short))
        return df

    def calculate_distance(self, recommended, history):
        recommended_articles = self.handlers.articles.get_multiple_by_id(recommended)
        recommended_complexities = [article.complexity for article in recommended_articles if article.complexity]
        r_mode = self.mode([self.discretize(complexity) for complexity in recommended_complexities])
        if r_mode:
            r_index = list(self.flesch_kincaid_map).index(r_mode)
        history_articles = self.handlers.articles.get_multiple_by_id(history)
        history_complexities = [article.complexity for article in history_articles if article.complexity]
        h_mode = self.mode([self.discretize(complexity) for complexity in history_complexities])
        if h_mode:
            h_index = list(self.flesch_kincaid_map).index(h_mode)
        try:
            return (r_index - h_index)/4
        except UnboundLocalError:
            return 0

    def calculate_all_distances(self, history):
        history_articles = self.handlers.articles.get_multiple_by_id(history)
        history_complexities = pd.Series([article.complexity for article in history_articles if article.complexity])
        return history_complexities.mean(), history_complexities.std()

    @staticmethod
    def visualize_content(df):
        """
        For each recommender type, create a scatter plot of all values found and an average line
        """
        print("===CONTENT PERSONALIZATION===")
        print(df.groupby('type')['cosine_mean'].mean())
        print(df.groupby('type')['cosine_std'].std())
        # prepare dataframe for visualization
        # df['date'] = pd.to_datetime(df['date'], format="%d-%m-%Y")
        # df = df.sort_values('date', ascending=True)
        # unique_types = df.type.unique()
        # fig, axes = plt.subplots(ncols=len(unique_types), sharey=True, figsize=(9, 3))
        # # iterate over different types of recommendations
        # for i, recommendation_type in enumerate(unique_types):
        #     ax = axes[i]
        #     ax.set_title(recommendation_type)
        #     df1 = df[df['type'] == recommendation_type]
        #     df_mean = df1.groupby(df1.date)['cosine'].mean()
        #     # create plots
        #     ax.scatter(x='date', y='cosine', data=df1)
        #     ax.plot(df_mean, '*-y')
        # plt.draw()

    @staticmethod
    def visualize_style(df):
        print("===STYLE PERSONALIZATION===")
        print(df.groupby('type')['distance_mean'].mean())
        print(df.groupby('type')['distance_std'].mean())
        # prepare dataframe for visualization
        # df = df.sort_values('date', ascending=True)
        # df['date'] = pd.to_datetime(df['date'], format="%d-%m-%Y")
        # unique_types = df.type.unique()
        # _, axes = plt.subplots(ncols=len(unique_types), sharey=True, figsize=(9, 3))
        # # iterate over different types of recommendations
        # for i, recommendation_type in enumerate(unique_types):
        #     ax = axes[i]
        #     ax.set_title(recommendation_type)
        #     df1 = df[df['type'] == recommendation_type]
        #     df_mean = df1.groupby(df1.date)['distance'].mean()
        #     # create plots
        #     ax.scatter(x='date', y='distance', data=df1)
        #     ax.plot(df_mean, '*-y')
        # plt.draw()
