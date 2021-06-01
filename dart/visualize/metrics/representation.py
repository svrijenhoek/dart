import numpy as np
import matplotlib.pyplot as plt
from math import log


class Representation:

    """
    Calculates Representation of entities linked to different political parties using KL Divergence.
    Currently the implementation is only suitable for the Participatory model, where we compare the party distribution
    in the recommendations to the one that was available in the pool. For the Deliberative and Critical models we also
    need to implement comparison with an equal and "pool inverse" distribution
    """

    def __init__(self, config):
        self.config = config
        self.party_data = {}
        # to do: add support for English parties. Also disitnguish between UK/US, fix by adding a country parameter
        # beside the language parameter?

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
        # should think of something for "Independent",
        elif self.config["language"] == "english":
            self.political_parties = np.array([
                ["Democrat", "Democratic Party"],
                ["Republican", "Republican Party"],
                #["", "Independent"],
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
        persons = filter(lambda x: x['label'] == 'PERSON', entities)
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
        bars2 = [data['npa'][label] for label in labels]
        bars3 = [data['lstur'][label] for label in labels]
        # bars4 = [data['political'][label] for label in labels]
        # bars4 = [data['political'][label] for label in labels]
        # Set position of bar on X axis
        r1 = np.arange(len(bars1))
        r2 = [x + barWidth for x in r1]
        r3 = [x + barWidth for x in r2]
        # r4 = [x + barWidth for x in r3]
        # Make the plot
        plt.bar(r1, bars1, width=barWidth, edgecolor='white', label='random')
        plt.bar(r2, bars2, width=barWidth, edgecolor='white', label='npa')
        plt.bar(r3, bars3, width=barWidth, edgecolor='white', label='lstur')
        # plt.bar(r4, bars4, width=barWidth, edgecolor='white', label='political')
        # Add xticks on the middle of the group bars
        plt.xlabel('parties', fontweight='bold')
        plt.xticks([r + barWidth for r in range(len(bars1))], labels, rotation='vertical')

    def calculate(self, pool, recommendation):
        pool_vector = self.make_vector(pool)
        recommendation_vector = self.make_vector(recommendation)
        distance = self.kullback_leibler(pool_vector, recommendation_vector, )
        return np.mean(distance)
