import string

import dart.handler.NLP.annotator
import dart.handler.NLP.textpipe_handler
import dart.handler.other.openstreetmap
import dart.handler.other.wikidata
import dart.Util


class Enricher:

    def __init__(self, handlers):
        self.handlers = handlers
        self.annotator = dart.handler.NLP.annotator.Annotator()
        self.textpipe = dart.handler.NLP.textpipe_handler.Textpipe()
        self.openstreetmap = dart.handler.other.openstreetmap.OpenStreetMap()
        self.wikidata = dart.handler.other.wikidata.WikidataHandler()
        self.printable = set(string.printable)

        try:
            self.known_locations = dart.Util.read_json_file('../../output/known_locations.json')
        except FileNotFoundError:
            self.known_locations = {}
        try:
            self.known_persons = dart.Util.read_json_file('../../output/known_persons.json')
        except FileNotFoundError:
            self.known_persons = {}

    def save_known_entities(self):
        dart.Util.write_to_json('output/known_locations.json', self.known_locations)
        dart.Util.write_to_json('output/known_persons.json', self.known_persons)

    def retrieve_occupation(self, entity):
        name = entity['text']
        parties = positions = []
        if name not in self.known_persons:
            # get list of all entity's known occupations
            occupations = self.wikidata.get_occupations(name)
            # if one of the occupations is 'politicus', retrieve party and position
            if 'politicus' in occupations:
                parties = self.wikidata.get_party(name)
                positions = self.wikidata.get_positions(name)
            self.known_persons[name] = {'occupations': occupations, 'parties': parties, 'positions': positions}
        else:
            occupations = self.known_persons[name]['occupations']
            parties = self.known_persons[name]['parties']
            positions = self.known_persons[name]['positions']
        if occupations:
            entity['occupations'] = occupations
            if parties:
                entity['parties'] = parties
            if positions:
                entity['positions'] = positions
        return entity

    def retrieve_geolocation(self, entity):
        name = entity['text']
        place = ''.join(filter(lambda x: x in self.printable, name))
        if len(place) > 2 and '|' not in place and place.lower() != 'None'.lower():
            if place not in self.known_locations:
                try:
                    # retrieve the coordinates from OpenStreetMap
                    lat, lon, country_code = self.openstreetmap.get_coordinates(str(place))
                    self.known_locations[place] = [country_code, lat, lon]
                    entity['location'] = {
                        'lat': lat,
                        'lon': lon
                    }
                    entity['country_code'] = country_code
                except TypeError:
                    print(place)
        return entity

    def annotate_entities(self, entities):
        annotated_entities = []
        for entity in entities:
            if entity['label'] == 'PER':
                entity = self.retrieve_occupation(entity)
            if entity['label'] == 'LOC':
                entity = self.retrieve_geolocation(entity)
            annotated_entities.append(entity)
        return annotated_entities

    def enrich_all(self):
        recommendations = self.handlers.recommendations.get_all_recommendations()
        for recommendation in recommendations:
            article = self.handlers.articles.get_by_id(recommendation.article_id)
            print(article.title)
            if not article.entities:
                doc, entities, tags = self.annotator.annotate(article.text)
                enriched_entities = self.annotate_entities(entities)
                self.handlers.articles.update(article.id, 'tags', tags)
                self.handlers.articles.update(article.id, 'entities', enriched_entities)
            if not article.nsentences or not article.nwords or not article.complexity:
                # rewrite
                nwords, nsentences, complexity = self.textpipe.analyze(article.text)
                self.handlers.articles.update(article.id, 'nwords', nwords)
                self.handlers.articles.update(article.id, 'nsentences', nsentences)
                self.handlers.articles.update(article.id, 'complexity', complexity)
        self.save_known_entities()



