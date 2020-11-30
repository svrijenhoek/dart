import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import Counter
from math import log
import dart.visualize.visualize as visualize


class Representation:

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config
        self.party_data = {}

        self.users = self.handlers.users.get_all_users()
        if self.config['test_size'] > 0:
            self.users = self.users[1:self.config['test_size']]

        # to do: add support for English parties. Also disitnguish between UK/US, fix by adding a country parameter
        # beside the language parameter.
        if self.config["language"] == "german":
            self.political_parties = np.array([
                ["CDU", "Christlich Demokratische Union Deutschlands"],
                ["SPD", "Sozialdemokratische Partei Deutschlands"],
                ["AfD", "Alternative für Deutschland"],
                ["FDP", "Freie Demokratische Partei"],
                ["LINKE", "Die Linke"],
                ["GRÜNE", "Bündnis 90/Die Grünen"],
                ["CSU", "Christlich-Soziale Union in Bayern"]
            ])
        elif self.config["language"] == "dutch":
            self.political_parties = np.array([
                ["CDA", "Christen-Democratisch Appèl"],
                ["CU", "ChristenUnie"],
                ["D66", "Democraten 66"],
                ["FvD", "Forum voor Democratie"],
                ["GL", "GroenLinks"],
                ["PvdA", "Partij van de Arbeid"],
                ["PvdD", "Partij voor de Dieren"],
                ["PVV", "Partij voor de Vrijheid"],
                ["SGP", "Staatkundig Gereformeerde Partij"],
                ["SP", "Socialistische Partij"],
                ["VVD", "Volkspartij voor Vrijheid en Democratie"],
                ["50Plus", "50Plus"],
                ["DENK", "Denk"],
            ])

    @staticmethod
    def in_entities(entities, party):
        """
        Check if the political party is mentioned in line with the article's entities.
        This means checking the political party that mentioned politicians belong to. Could be extended to also checking
        mentioned organisations, but checking the fulltext for this proved more efficient.
        """
        short_party = party[0]
        full_party = party[1]
        # only consider entities of type person
        persons = filter(lambda x: x['label'] == 'PER', entities)
        for person in persons:
            # if the person has a property 'party' (this avoids checking this value for people that are not politicians)
            if 'parties' in person:
                if short_party in person['parties'] or full_party in person['parties']:
                    return True
        organisations = filter(lambda x: x['label'] == 'ORG', entities)
        for organisation in organisations:
            # if the person has a property 'party' (this avoids checking this value for people that are not politicians)
            if short_party == organisation['text'] or full_party == organisation['text']:
                return True
        return False

    @staticmethod
    def kullback_leibler(p, q):
        k_l = 0.0
        for i in range(len(p)):
            p_i = p[i]
            q_i = q[i]
            if q_i != 0.0:
                try:
                    k_l += (p_i * log(p_i / q_i))
                except ValueError:
                    pass
        return k_l

    def calculate_distance(self, recommendation_vectors, pool_vector, recommendation_type):
        distances = []
        # for each recommendation set
        for recommendation_vector in recommendation_vectors:
            distance = self.kullback_leibler(pool_vector, recommendation_vector, )
            diff = np.array(recommendation_vector) - np.array(pool_vector)
            distances.append(distance)
            # keep track of the absolute differences for each party
            for i, party in enumerate(self.political_parties):
                self.party_data[recommendation_type][party[0]] += diff[i]
        return distances

    def make_vector(self, articles):
        """
        Create a vector representing the relative representation of political parties in articles
        """
        all_vector = [0]*len(self.political_parties)
        for article in articles:
            article_vector = [0]*len(self.political_parties)
            # for each party specified in the configuration file
            for ix, party in enumerate(self.political_parties):
                # check if the party is either mentioned in one of the article's articles or mentioned in the text
                if self.in_entities(article.entities, party): # or self.in_fulltext(article.text, party):
                    # binary approach; being mentioned once is enough
                    article_vector[ix] = 1
            all_vector = [x + y for x, y in zip(all_vector, article_vector)]
        # normalize for the length of the article
        sum = np.sum(all_vector)
        if sum == 0:
            # return a perfectly even distribution
            return [1/len(self.political_parties)]*len(self.political_parties)
        else:
            output = [x/sum for x in all_vector]
            return output

    def get_recommendation_vectors(self, date, recommendation_type):
        all_vectors = []
        # for each user
        for user in self.users:
            # get the recommendations issued to this user
            recommendation = self.handlers.recommendations.get_recommendations_to_user_at_date(
                user.id,
                date,
                recommendation_type)
            if recommendation:
                articles = self.handlers.articles.get_multiple_by_id(recommendation[0].articles)
                vector = self.make_vector(articles)
                all_vectors.append(vector)
        return all_vectors

    def execute(self):
        """
        Iterate over all dates and recommendation types to calculate distance in attention distributions.
        Visualize output.
        """
        data = []
        for date in self.config["recommendation_dates"]:
            # retrieve all articles in the specified time range
            upper = datetime.strptime(date, '%Y-%m-%d')
            lower = upper - timedelta(days=self.config["recommendation_range"])
            pool = self.handlers.articles.get_all_in_timerange(lower, upper)
            # make a vector of party representation in the pool
            pool_vector = self.make_vector(pool)
            # for each recommendation type (custom, most_popular, random)
            for recommendation_type in self.handlers.recommendations.get_recommendation_types():
                self.party_data[recommendation_type] = Counter()
                recommendation_vectors = self.get_recommendation_vectors(date, recommendation_type)
                distances = self.calculate_distance(recommendation_vectors, pool_vector, recommendation_type)
                data.append({'date': date, 'type': recommendation_type, 'distance': np.mean(distances)})
        df = pd.DataFrame(data)
        self.visualize(df)

        # normalize to account for different sizes of recommendations
        for recommendation_type in self.party_data:
            len_rec_type = len(df[df['type'] == recommendation_type].index)
            for party in self.party_data[recommendation_type]:
                self.party_data[recommendation_type][party] = self.party_data[recommendation_type][party] / len_rec_type
        self.visualize_party(self.party_data)

    @staticmethod
    def visualize(df):
        visualize.Visualize.print_mean(df, 'distance')
        visualize.Visualize.plot(df, 'distance', "Representation")

    def visualize_party(self, data):
        """
        Bar plot visualizing for each party how often they are mentioned significantly more or less than was to be
        expected from the pool
        """
        plt.figure("Representation (diff)")
        labels = self.political_parties[:, 0]
        # set width of bar
        barWidth = 0.20

        for recommendation_type in data:
            for label in labels:
                if label not in data[recommendation_type]:
                    data[recommendation_type][label] = 0

        # set height of bar
        bars1 = [data['random'][label] for label in labels]
        bars2 = [data['custom'][label] for label in labels]
        bars3 = [data['most_popular'][label] for label in labels]
        bars4 = [data['political'][label] for label in labels]
        # bars4 = [data['political'][label] for label in labels]

        # Set position of bar on X axis
        r1 = np.arange(len(bars1))
        r2 = [x + barWidth for x in r1]
        r3 = [x + barWidth for x in r2]
        r4 = [x + barWidth for x in r3]

        # Make the plot
        plt.bar(r1, bars1, width=barWidth, edgecolor='white', label='random')
        plt.bar(r2, bars2, width=barWidth, edgecolor='white', label='custom')
        plt.bar(r3, bars3, width=barWidth, edgecolor='white', label='most_popular')
        plt.bar(r4, bars4, width=barWidth, edgecolor='white', label='political')

        # Add xticks on the middle of the group bars
        plt.xlabel('parties', fontweight='bold')
        plt.xticks([r + barWidth for r in range(len(bars1))], labels, rotation='vertical')

        # Create legend & Show graphic
        plt.legend()
        plt.show()



