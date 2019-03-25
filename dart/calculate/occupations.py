from dart.models.Article import Article
from dart.handler.elastic.article_handler import ArticleHandler
from dart.handler.elastic.recommendation_handler import RecommendationHandler
from dart.handler.elastic.connector import Connector
from dart.handler.other.wikidata import WikidataHandler
from collections import defaultdict
import json
import sys
import elasticsearch
import logging


class Occupations:

    """
    Class that retrieves the occupations of all entities of type 'Person' from Wikidata. If this returns a
    'politicus' (Dutch politician), it will retrieve their parties and current position.

    Maintains a list of 'known entities' to save computation time.
    """

    def __init__(self):
        self.known_entities = {}
        self.searcher = ArticleHandler()
        self.recommendation_handler = RecommendationHandler()
        self.connector = Connector()
        self.wikidata = WikidataHandler()
        self.module_logger = logging.getLogger('occupations')

    def add_document(self, doctype, user, date, doc_id, key, label, frequency):
        doc = {
            'type': doctype,
            'date': date,
            'user': user,
            'article_id': doc_id,
            key: {'name': label, 'frequency': frequency}
        }
        body = json.dumps(doc)
        try:
            self.connector.add_document('occupations', '_doc', body)
        except elasticsearch.exceptions.RequestError:
            self.module_logger.error('Retrieving Wikidata information failed')

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
        """
        all_occupations = all_parties = all_positions = defaultdict(int)
        for entity in doc.entities:
            if entity['label'] == 'PER':
                name = entity['text']
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
        df = self.recommendation_handler.initialize()
        # for each type of recommendation
        for recommendation_type in df.recommendation_type.unique():
            self.module_logger.info("Calculating 'occupations for "+recommendation_type)
            df1 = df[df.recommendation_type == recommendation_type]
            # iterate over each recommended article
            for _, row in df1.iterrows():
                # retrieve the actual document
                document = Article(self.searcher.get_by_id(row.id))
                occupations, parties, positions = self.analyze_document(document)
                # store how many times the user has seen a particular occupation/party/position in each recommendation
                for occupation in occupations:
                    frequency = occupations[occupation]
                    self.add_document(recommendation_type, row.user_id, row.date, row.id,
                                      'occupation', occupation, frequency)
                for party in parties:
                    frequency = parties[party]
                    self.add_document(recommendation_type, row.user_id, row.date, row.id,
                                      'party', party, frequency)
                for position in positions:
                    frequency = positions[position]
                    self.add_document(recommendation_type, row.user_id, row.date, row.id,
                                      'position', position, frequency)


