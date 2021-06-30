from collections import Counter


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

                self.gender_scores[article.id] = {'majority': article_majority, 'minority': article_minority}
            majority += article_majority
            minority += article_minority
        return minority, majority

    def calculate(self, pool, recommendation):
        pool_ethnicity = self.get_ethnicity_score(pool)
        pool_gender = self.get_gender_score(pool)
        recommendation_ethnicity = self.get_ethnicity_score(recommendation)
        recommendation_gender = self.get_gender_score(recommendation)

        ethnicity_inclusion = self.calculate_alternative_voices(pool_ethnicity, recommendation_ethnicity)
        gender_inclusion = self.calculate_alternative_voices(pool_gender, recommendation_gender)

        return ethnicity_inclusion, gender_inclusion
