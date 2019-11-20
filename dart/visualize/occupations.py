from collections import defaultdict
import logging


class OccupationCalculator:

    """
    Class that retrieves the occupations of all entities of type 'Person' from Wikidata. If this returns a
    'politicus' (Dutch politician), it will retrieve their parties and current position.

    Maintains a list of 'known entities' to save computation time.

    Naive approach to names and their variations.
    """

    def __init__(self, handlers):
        self.module_logger = logging.getLogger('occupations')
        self.handlers = handlers

    @staticmethod
    def count_occupations(entities):
        """
        count all occupations, and in case of politicians the parties and positions they hold
        >>> entities = [{"label": "PER", "parties": ["Democratische Partij"], "positions": ["president van de Verenigde Staten"], "occupations": ["staatsman", "politicus"], "frequency": 1}]
        >>> OccupationCalculator.count_occupations(entities)
        (defaultdict(<class 'int'>, {'staatsman': 1, 'politicus': 1}), defaultdict(<class 'int'>, {'Democratische Partij': 1}), defaultdict(<class 'int'>, {'president van de Verenigde Staten': 1}))
        """
        all_occupations = defaultdict(int)
        all_parties = defaultdict(int)
        all_positions = defaultdict(int)
        persons = filter(lambda x: x['label'] == 'PER', entities)
        for person in persons:
            # update frequency lists
            try:
                for occupation in person['occupations']:
                    all_occupations[occupation] += person['frequency']
            except KeyError:
                pass
            try:
                for party in person['parties']:
                    all_parties[party] += person['frequency']
            except KeyError:
                pass
            try:
                for position in person['positions']:
                    all_positions[position] += person['frequency']
            except KeyError:
                pass
        return all_occupations, all_parties, all_positions

    def execute(self):
        """
        All recommendations are retrieved, and for each known recommendation type the Named Entities of type person
        are retrieved. An overview with the frequencies of each occupation is constructed and stored in Elasticsearch.
        """
        # data frame with information about each recommended article
        df = self.handlers.recommendations.initialize()
        # for each type of recommendation
        for recommendation_type in df.recommendation_type.unique():
            self.module_logger.info("Calculating 'occupations for "+recommendation_type)
            df1 = df[df.recommendation_type == recommendation_type]
            count = 0
            # iterate over each recommended article
            for _, row in df1.iterrows():
                # retrieve the actual document
                document = self.handlers.articles.get_by_id(row.id)
                occupations, parties, positions = self.count_occupations(document.entities)

                # store how many times the user has seen a particular occupation/party/position in each recommendation
                for occupation in occupations:
                    frequency = occupations[occupation]
                    self.handlers.output.add_occupation_document(recommendation_type, row.user_id, row.date, row.id,
                                                                 'occupation', occupation, frequency)
                for party in parties:
                    frequency = parties[party]
                    self.handlers.output.add_occupation_document(recommendation_type, row.user_id, row.date, row.id,
                                                                 'party', party, frequency)
                for position in positions:
                    frequency = positions[position]
                    self.handlers.output.add_occupation_document(recommendation_type, row.user_id, row.date, row.id,
                                                                 'position', position, frequency)
                count += 1
                if count % 1000 == 0:
                    print(count)
