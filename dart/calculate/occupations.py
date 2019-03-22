from dart.models.Article import Article
from dart.handler.elastic.article_handler import ArticleHandler
from dart.handler.elastic.recommendation_handler import RecommendationHandler
from dart.handler.elastic.connector import Connector
from dart.handler.other.wikidata import WikidataHandler
import json
import sys
import elasticsearch


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

    @staticmethod
    def update_list(o, l):
        for occupation in o:
            if occupation in l:
                l[occupation] = l[occupation]+1
            else:
                l[occupation] = 1
        return l

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
            print(doc)
            sys.exit()

    def analyze_entity(self, label):
        entity_occupations = self.wikidata.get_occupations(label)
        if 'politicus' in entity_occupations:
            entity_parties = self.wikidata.get_party(label)
            entity_positions = self.wikidata.get_positions(label)
        else:
            entity_parties = entity_positions = {}
        return entity_occupations, entity_parties, entity_positions

    def analyze_document(self, doc):
        all_occupations = all_parties = all_positions = {}
        for entity in doc.entities:
            if entity['label'] == 'PER':
                name = entity['text']
                if name not in self.known_entities:
                    entity_occupations, entity_parties, entity_positions = self.analyze_entity(name)
                    all_occupations = self.update_list(entity_occupations, all_occupations)
                    self.known_entities[name] = {'occupations': entity_occupations, 'parties': entity_parties,
                                                 'positions': entity_positions}
                else:
                    entry = self.known_entities[entity['text']]
                    entity_occupations = entry['occupations']
                    entity_parties = entry['parties']
                    entity_positions = entry['positions']
                all_occupations = self.update_list(entity_occupations, all_occupations)
                all_parties = self.update_list(entity_parties, all_parties)
                all_positions = self.update_list(entity_positions, all_positions)
        return all_occupations, all_parties, all_positions

    def execute(self):
        df = self.recommendation_handler.initialize()
        for recommendation_type in df.recommendation_type.unique():
            df1 = df[df.recommendation_type == recommendation_type]
            for index, row in df1.iterrows():
                document = Article(self.searcher.get_by_id(row.id))
                occupations, parties, positions = self.analyze_document(document)
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


def main(argv):
    run = Occupations()
    run.execute()


if __name__ == "__main__":
    main(sys.argv[1:])

