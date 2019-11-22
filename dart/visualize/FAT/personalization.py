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
        cos = dart.handler.NLP.cosine_similarity.CosineSimilarity()
        recommendation_types = self.handlers.recommendations.get_recommendation_types()
        data = []
        for user in self.handlers.users.get_all_users():
            for recommendation_type in recommendation_types:
                for date in self.config["recommendation_dates"]:
                    # retrieve all articles recommended at that date
                    recommended_ids = user.reading_history[recommendation_type][date]
                    if recommended_ids:
                        # retrieve the reading history at that date
                        strp_date = datetime.strptime(date, '%d-%m-%Y')
                        reading_history = user.select_reading_history(strp_date, recommendation_type)
                        # calculate the average cosine similarity
                        median_cosine = cos.calculate_cosine_similarity(recommended_ids, reading_history)
                        # cosine = cos.calculate_cosine_experiment(recommended_ids, reading_history)
                        distance = self.calculate_distance(recommended_ids, reading_history)
                        data.append({"user": user.id, "type": recommendation_type, "date": date, "cosine": median_cosine,
                                     "distance": distance})
        # create dataframe of results
        df = pd.DataFrame(data, columns=["user", "type", "date", "cosine", "distance"])
        return df

    def calculate_distance(self, recommended, history):
        recommended_articles = self.handlers.articles.get_multiple_by_id(recommended)
        recommended_complexities = [article.complexity for article in recommended_articles]
        r_mode = self.mode([self.discretize(complexity) for complexity in recommended_complexities])
        if r_mode:
            r_index = list(self.flesch_kincaid_map).index(r_mode)
        history_articles = self.handlers.articles.get_multiple_by_id(history)
        history_complexities = [article.complexity for article in history_articles]
        h_mode = self.mode([self.discretize(complexity) for complexity in history_complexities])
        if h_mode:
            h_index = list(self.flesch_kincaid_map).index(h_mode)
        try:
            return (r_index - h_index)/4
        except UnboundLocalError:
            return 0

    @staticmethod
    def visualize_content(df):
        """
        For each recommender type, create a scatter plot of all values found and an average line
        """
        print("===CONTENT PERSONALIZATION===")
        print(df.groupby('type')['cosine'].mean())
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
            df_mean = df1.groupby(df1.date)['cosine'].mean()
            # create plots
            ax.scatter(x='date', y='cosine', data=df1)
            ax.plot(df_mean, '*-y')
        plt.draw()

    @staticmethod
    def visualize_style(df):
        print("===STYLE PERSONALIZATION===")
        print(df.groupby('type')['distance'].mean())
        # prepare dataframe for visualization
        df = df.sort_values('date', ascending=True)
        df['date'] = pd.to_datetime(df['date'], format="%d-%m-%Y")
        unique_types = df.type.unique()
        _, axes = plt.subplots(ncols=len(unique_types), sharey=True, figsize=(9, 3))
        # iterate over different types of recommendations
        for i, recommendation_type in enumerate(unique_types):
            ax = axes[i]
            ax.set_title(recommendation_type)
            df1 = df[df['type'] == recommendation_type]
            df_mean = df1.groupby(df1.date)['distance'].mean()
            # create plots
            ax.scatter(x='date', y='distance', data=df1)
            ax.plot(df_mean, '*-y')
        plt.draw()
