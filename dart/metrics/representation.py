import numpy as np
from dart.external.kl_divergence import compute_kl_divergence


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

    def make_vector(self, articles):
        """
        Create a vector representing the relative representation of political parties in articles
        """
        # all_vector = [0]*len(self.political_parties)
        vector = {party[0]: 0 for party in self.political_parties}
        for article in articles:
            # for each party specified in the configuration file
            for ix, party in enumerate(self.political_parties):
                # check if the party is either mentioned in one of the article's entities or mentioned in the text
                if self.in_entities(article.entities, party): # or self.in_fulltext(article.text, party):
                    # binary approach; being mentioned once is enough
                    vector[party[0]] += 1
        return vector

    def calculate(self, pool, recommendation):
        pool_vector = self.make_vector(pool)
        recommendation_vector = self.make_vector(recommendation)
        return compute_kl_divergence(pool_vector, recommendation_vector)
