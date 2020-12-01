from textblob import TextBlob
from textblob_de import TextBlobDE
from textblob_nl import PatternTagger, PatternAnalyzer
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import dart.visualize.visualize as visualize


class Affect:

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config
        self.scores = {}
        self.language = self.config["language"]
        self.users = self.handlers.users.get_all_users()
        if self.config['test_size'] > 0:
            self.users = self.users[1:self.config['test_size']]

    def analyze(self, text):
        if self.language == 'dutch':
            blob = TextBlob(text, pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())
        elif self.language == 'english':
            blob = TextBlob(text)
        elif self.language == 'german':
            blob = TextBlobDE(text)
        return blob

    def get_affect_score(self, article):
        if article.id not in self.scores:
            # use sentiment analysis to retrieve a polarity score
            blob = self.analyze(article.text)
            polarity = blob.polarity
            self.scores[article.id] = abs(polarity)
        return self.scores[article.id]

    def get_pool_scores(self, date):
        # retrieve all articles in the specified time range
        upper = datetime.strptime(date, '%Y-%m-%d')
        lower = upper - timedelta(days=self.config["recommendation_range"])
        pool = self.handlers.articles.get_all_in_timerange(lower, upper)
        return np.mean([self.get_affect_score(article) for article in pool])

    def get_recommendation_scores(self, date, recommendation_type):
        scores = []
        # for each user
        for user in self.users:
            # get the recommendations issued to this user
            recommendation = self.handlers.recommendations.get_recommendations_to_user_at_date(
                user.id,
                date,
                recommendation_type)
            if recommendation:
                articles = self.handlers.articles.get_multiple_by_id(recommendation[0].articles)
                for article in articles:
                    affect = self.get_affect_score(article)
                    scores.append(affect)
        return scores

    def execute(self):
        data = []
        diff_data = []
        # when in test phase, only test with the specified number of users
        no_dates = len(self.config["recommendation_dates"])
        marker = no_dates/10
        for x, date in enumerate(self.config["recommendation_dates"]):
            if x % marker < 1:
                print(str(datetime.now()) + "\t\t\t{:.0f}% completed".format(x/no_dates*100))
            pool_scores = self.get_pool_scores(date)
            # for each recommendation type that is specified in the config file
            for recommendation_type in self.handlers.recommendations.get_recommendation_types():
                # affect scores
                recommendation_scores = self.get_recommendation_scores(date, recommendation_type)
                data.append({'date': date,
                             'type': recommendation_type,
                             'mean': np.mean(recommendation_scores),
                             'std': np.std(recommendation_scores)})
                diff_data.append({'date': date,
                                  'type': recommendation_type,
                                  'mean': np.mean(recommendation_scores) - np.mean(pool_scores),
                                  'std': np.std(recommendation_scores) - np.std(pool_scores)})
        df = pd.DataFrame(data)
        self.visualize(df, "Affect")
        df = pd.DataFrame(diff_data)
        self.visualize(df, "Affect (diff)")

    @staticmethod
    def visualize(df, title):
        visualize.Visualize.print_mean(df)
        visualize.Visualize.plot(df, title)
