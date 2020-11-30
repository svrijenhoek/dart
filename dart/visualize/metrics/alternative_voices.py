from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import Counter

import dart.visualize.visualize as visualize


class AlternativeVoices:

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config

        self.users = self.handlers.users.get_all_users()
        if self.config['test_size'] > 0:
            self.users = self.users[1:self.config['test_size']]

        self.ethnicity_scores = {}
        self.gender_scores = {}

        self.minorities = Counter()
        self.majorities = Counter()
        self.irrelevants = Counter()

    def get_ethnicity_score(self, articles, store=False):
        majority = 0
        minority = 0
        for article in articles:
            article_majority = 0
            article_minority = 0
            if article.id in self.ethnicity_scores:
                article_majority = self.ethnicity_scores[article.id]['majority']
                article_minority = self.ethnicity_scores[article.id]['minority']
            else:
                persons = filter(lambda x: x['label'] == 'PER', article.entities)
                for person in persons:
                    if 'citizen' in person and "Germany" in person['citizen']:
                        if 'ethnicity' in person:
                            if 'Germans' in person['ethnicity'] or person['ethnicity'] == []:
                                article_majority += 1
                                if store: self.majorities[person['text']] += 1
                            else:
                                article_minority += 1
                                if store: self.minorities[person['text']] += 1
                        else:
                            if 'place_of_birth' in person:
                                if 'Germany' in person['place_of_birth']:
                                    article_majority += 1
                                    if store: self.majorities[person['text']]
                                else:
                                    article_minority += 1
                                    if store: self.minorities[person['text']]
                    else:
                        if store: self.irrelevants[person['text']] += 1
                self.ethnicity_scores[article.id] = {'majority': article_majority, 'minority': article_minority}
            majority += article_majority
            minority += article_minority
        return minority, majority

    @staticmethod
    def calculate_alternative_voices(pool_scores, recommendation_scores):
        # number of people in the protected group in the recommendation
        pi_plus = recommendation_scores[0]
        # number of people in the unprotected group in the recommendation
        pi_minus = recommendation_scores[1]
        # number of people in the protected group in the pool
        l_plus = pool_scores[0]
        # number of people in the unprotected group in the pool
        l_minus = pool_scores[1]
        if pi_plus == 0 or pi_minus == 0 or l_plus == 0 or l_minus == 0:
            return 0
        else:
            score = (pi_plus/l_plus)/(pi_minus/l_minus)
            return score

    def get_gender_score(self, articles, store=False):
        majority = 0
        minority = 0
        for article in articles:
            article_majority = 0
            article_minority = 0
            if article.id in self.gender_scores:
                article_majority = self.gender_scores[article.id]['majority']
                article_minority = self.gender_scores[article.id]['minority']
            else:
                persons = filter(lambda x: x['label'] == 'PER', article.entities)
                for person in persons:
                    if 'citizen' in person and "Germany" in person['citizen']:
                        if 'gender' in person:
                            if 'male' in person['gender']:
                                article_majority += 1
                                if store: self.majorities[person['text']] += 1
                            else:
                                article_minority += 1
                                if store: self.minorities[person['text']] += 1

                    else:
                        if store: self.irrelevants[person['text']] += 1

                self.gender_scores[article.id] = {'majority': article_majority, 'minority': article_minority}
            majority += article_majority
            minority += article_minority
        return minority, majority

    def execute(self):
        """
        Iterate over all dates and recommendation types to calculate distance in attention distributions.
        Visualize output.
        """
        ethnicity_data = []
        gender_data = []
        for date in self.config["recommendation_dates"]:
            print(date)
            # retrieve all articles in the specified time range
            upper = datetime.strptime(date, '%Y-%m-%d')
            lower = upper - timedelta(days=self.config["recommendation_range"])
            pool = self.handlers.articles.get_all_in_timerange(lower, upper)
            pool_ethnicity = self.get_ethnicity_score(pool, True)
            pool_gender = self.get_gender_score(pool)
            # for each recommendation type (custom, most_popular, random)
            for recommendation_type in self.handlers.recommendations.get_recommendation_types():
                print(recommendation_type)
                ethnicity_inclusion_scores = []
                gender_inclusion_scores = []
                for user in self.users:
                    # get the recommendations issued to this user
                    recommendation = self.handlers.recommendations.get_recommendations_to_user_at_date(
                        user.id,
                        date,
                        recommendation_type)
                    if recommendation:
                        articles = self.handlers.articles.get_multiple_by_id(recommendation[0].articles)
                        recommendation_ethnicity = self.get_ethnicity_score(articles)
                        ethnicity_inclusion = self.calculate_alternative_voices(pool_ethnicity, recommendation_ethnicity)
                        ethnicity_inclusion_scores.append(ethnicity_inclusion)
                        recommendation_gender = self.get_gender_score(articles)
                        gender_inclusion = self.calculate_alternative_voices(pool_gender, recommendation_gender)
                        gender_inclusion_scores.append(gender_inclusion)
                ethnicity_data.append({'date': date, 'type': recommendation_type,
                                       'mean': np.mean(ethnicity_inclusion_scores),
                                       'std': np.std(ethnicity_inclusion_scores)})
                gender_data.append({'date': date, 'type': recommendation_type,
                                   'mean': np.mean(gender_inclusion_scores),
                                   'std': np.std(gender_inclusion_scores)})
        ethnicity_df = pd.DataFrame(ethnicity_data)
        gender_df = pd.DataFrame(gender_data)
        self.visualize(ethnicity_df, gender_df)

    def visualize(self, ethnicity_df, gender_df):
        visualize.Visualize.print_mean(ethnicity_df)
        visualize.Visualize.plot(ethnicity_df, "Inclusion (ethnicity)")

        visualize.Visualize.print_mean(gender_df)
        visualize.Visualize.plot(gender_df, "Inclusion (gender)")

        # visualize.Visualize.print_mean(gender_df)
        # visualize.Visualize.plot(gender_df, "Inclusion (gender)")
