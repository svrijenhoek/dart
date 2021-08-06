from collections import Counter
from dart.external.discount import harmonic_number
from dart.external.kl_divergence import compute_kl_divergence


class AlternativeVoices:
    """
    Class that calculates the number of mentions of minority vs majority people. In the current implementation, what
    entails a minority / majority is hardcoded. In this case, for the implementation for a German media company,
    we calculate both minority/majority of gender and ethnicity. In both cases, we only consider German citizens.
    The required information is obtained by running Named Entity Recognition on a text and retrieving additional
    information about the identified persons from Wikidata.
    Gender:
        majority: male
        minority: non-male
    Ethnicity:
       majority: people with a 'United States' ethnicity or place of birth
       minority: other
    Actual calculation is done following the formula specified in Equation 8 from http://proceedings.mlr.press/v81/burke18a.html
    We recognize there are a multitude of problems with this approach, and welcome suggestions for better ones.
    """

    def __init__(self):
        self.ethnicity_scores = {}
        self.gender_scores = {}

        self.minorities = Counter()
        self.majorities = Counter()
        self.irrelevants = Counter()

    def get_ethnicity_score(self, article, store):
        article_majority = 0
        article_minority = 0
        if article.id in self.ethnicity_scores:
            article_majority = self.ethnicity_scores[article.newsid]['majority']
            article_minority = self.ethnicity_scores[article.newsid]['minority']
        else:
            persons = filter(lambda x: x['label'] == 'PERSON', article.entities)
            for person in persons:
                if 'citizen' in person and "United States" in person['citizen']:
                    if 'ethnicity' in person:
                        if 'white people' in person['ethnicity'] or person['ethnicity'] == []:
                            article_majority += 1
                            if store: self.majorities[person['text']] += 1
                        else:
                            article_minority += 1
                            if store: self.minorities[person['text']] += 1
                    else:
                        if 'place_of_birth' in person:
                            if 'United States' in person['place_of_birth']:
                                article_majority += 1
                                if store: self.majorities[person['text']]
                            else:
                                article_minority += 1
                                if store: self.minorities[person['text']]
                else:
                    if store: self.irrelevants[person['text']] += 1
            self.ethnicity_scores[article.newsid] = {'majority': article_majority, 'minority': article_minority}
        return article_majority, article_minority

    def get_gender_score(self, article, store):
        article_minority = 0
        article_majority = 0
        if article.id in self.gender_scores:
            article_majority = self.gender_scores[article.newsid]['majority']
            article_minority = self.gender_scores[article.newsid]['minority']
        else:
            persons = filter(lambda x: x['label'] == 'PERSON', article.entities)
            for person in persons:
                if 'citizen' in person and "United States" in person['citizen']:
                    if 'gender' in person:
                        if 'male' in person['gender']:
                            article_majority += 1
                            if store: self.majorities[person['text']] += 1
                        else:
                            article_minority += 1
                            if store: self.minorities[person['text']] += 1

                else:
                    if store: self.irrelevants[person['text']] += 1

            self.gender_scores[article.newsid] = {'majority': article_majority, 'minority': article_minority}
        return article_majority, article_minority

    def get_dist(self, articles, value, adjusted=False):
        n = len(articles)
        count = 0
        sum_one_over_ranks = harmonic_number(n)
        distr = {0: 0, 1: 0}
        majority = 0
        minority = 0
        for indx, article in articles.iterrows():
            rank = count + 1
            if value == 'gender':
                article_majority, article_minority = self.get_gender_score(article, True)
            else:
                article_majority, article_minority = self.get_ethnicity_score(article, True)
            if article_minority > 0 and article_majority > 0:
                if adjusted:
                    prob_majority = article_majority / (article_majority+article_minority) * 1/rank/sum_one_over_ranks
                    prob_minority = article_minority / (article_majority+article_minority) * 1/rank/sum_one_over_ranks
                else:
                    prob_majority = article_majority / (article_majority+article_minority)
                    prob_minority = article_minority / (article_majority+article_minority)
                majority += prob_majority
                minority += prob_minority
            count += 1
        r = minority + majority
        if r > 0:
            distr[0] = minority / r
            distr[1] = majority / r
        return distr

    def calculate(self, pool, recommendation):
        pool_ethnicity = self.get_dist(pool, 'ethnicity', False)
        pool_gender = self.get_dist(pool, 'gender', False)
        recommendation_ethnicity = self.get_dist(recommendation, 'ethnicity', True)
        recommendation_gender = self.get_dist(recommendation, 'gender', True)

        ethnicity_inclusion = compute_kl_divergence(pool_ethnicity, recommendation_ethnicity)
        gender_inclusion = compute_kl_divergence(pool_gender, recommendation_gender)

        return ethnicity_inclusion, gender_inclusion
