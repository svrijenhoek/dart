from dart.handler.other.wikidata import WikidataHandler
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
        self.known_entities = {}
        self.wikidata = WikidataHandler()
        self.module_logger = logging.getLogger('occupations')
        self.handlers = handlers

    def analyze_entity(self, label):
        # get list of all entity's known occupations
        entity_occupations = self.wikidata.get_occupations(label)
        # if one of the occupations is 'politicus', retrieve party and position
        if 'politicus' in entity_occupations:
            entity_parties = self.wikidata.get_party(label)
            entity_positions = self.wikidata.get_positions(label)
        else:
            entity_parties = entity_positions = {}
        return entity_occupations, entity_parties, entity_positions

    def analyze_document(self, doc):
        """
        Retrieve all the named entities of type Person in a document. Compare each to a list of known entities. If this
        entity is not yet known, retrieve its information from Wikidata.

        occupations = Occupations()
        occupations.known_entities = []
        occupations.analyze_document(Article({'entities': [{'label': 'PER', 'text': 'Mark Rutte'}]}))
        ['politicus'], ['VVD'], ['minister president']
        """
        all_occupations = all_parties = all_positions = defaultdict(int)
        persons = filter(lambda x: x['label'] == 'PER', doc.entities)
        for person in persons:
            name = person['text']
            # if we don't know the occupation of this entity yet, retrieve from Wikidata
            if name not in self.known_entities:
                entity_occupations, entity_parties, entity_positions = self.analyze_entity(name)
                # add the newly retrieved information to the list of known entities
                self.known_entities[name] = {'occupations': entity_occupations, 'parties': entity_parties,
                                             'positions': entity_positions}
            # if we do know the entity, update the frequency list with this information
            else:
                entry = self.known_entities[name]
                entity_occupations = entry['occupations']
                entity_parties = entry['parties']
                entity_positions = entry['positions']
            # update frequency lists
            for occupation in entity_occupations:
                all_occupations[occupation] += 1
            for party in entity_parties:
                all_parties[party] += 1
            for position in entity_positions:
                all_positions[position] += 1
        return all_occupations, all_parties, all_positions

    def execute(self):
        """
        All recommendations are retrieved, and for each known recommendation type the Named Entities of type person
        are retrieved. An overview with the frequencies of each occupation is constructed and stored in Elasticsearch.
        """
        # data frame with information about each recommended article
        df = self.handlers['recommendation_handler'].initialize()
        # for each type of recommendation
        for recommendation_type in df.recommendation_type.unique():
            self.module_logger.info("Calculating 'occupations for "+recommendation_type)
            df1 = df[df.recommendation_type == recommendation_type]
            # iterate over each recommended article
            for _, row in df1.iterrows():
                # retrieve the actual document
                document = self.handlers['article_handler'].get_by_id(row.id)
                occupations, parties, positions = self.analyze_document(document)
                # store how many times the user has seen a particular occupation/party/position in each recommendation
                for occupation in occupations:
                    frequency = occupations[occupation]
                    self.handlers['output_handler'].add_occupation_document(recommendation_type, row.user_id, row.date, row.id,
                                      'occupation', occupation, frequency)
                for party in parties:
                    frequency = parties[party]
                    self.handlers['output_handler'].add_occupation_document(recommendation_type, row.user_id, row.date, row.id,
                                      'party', party, frequency)
                for position in positions:
                    frequency = positions[position]
                    self.handlers['output_handler'].add_occupation_document(recommendation_type, row.user_id, row.date, row.id,
                                      'position', position, frequency)
