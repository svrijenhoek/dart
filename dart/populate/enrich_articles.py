import string
from ethnicolr import pred_census_ln
import pandas as pd

import dart.handler.NLP.annotator
import dart.handler.NLP.textpipe_handler
import dart.handler.other.openstreetmap
import dart.handler.other.wikidata
import dart.Util

import sys


class Enricher:

    def __init__(self, handlers, metrics):
        self.handlers = handlers
        self.metrics = metrics
        self.annotator = dart.handler.NLP.annotator.Annotator()
        self.textpipe = dart.handler.NLP.textpipe_handler.Textpipe()
        self.openstreetmap = dart.handler.other.openstreetmap.OpenStreetMap()
        self.wikidata = dart.handler.other.wikidata.WikidataHandler()
        self.printable = set(string.printable)
        self.spacy_tags = ['DET', 'ADP', 'PRON']

        try:
            self.known_locations = dart.Util.read_json_file('output/known_locations.json')
        except FileNotFoundError:
            self.known_locations = {}
        try:
            self.known_persons = dart.Util.read_json_file('output/known_persons.json')
        except FileNotFoundError:
            self.known_persons = {}

    def save_known_entities(self):
        dart.Util.write_to_json('output/known_locations.json', self.known_locations)
        dart.Util.write_to_json('output/known_persons.json', self.known_persons)

    def retrieve_occupation(self, entity):
        name = entity['text']
        parties = []
        positions = []
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

    def retrieve_ethnicity(self, entity):
        name = entity['text']
        try:
            entity['ethnicity'] = self.known_persons[name]['ethnicity']
            entity['gender'] = self.known_persons[name]['gender']
        except KeyError:
            person_data = self.wikidata.get_person_data(name)
            if not person_data:
                split = name.split(" ")
                if len(split) > 1:
                    person_data = {'givenlabel': split[0], 'familylabel': split[-1], 'genderlabel': 'unknown'}
                else:
                    person_data = {'givenlabel': '', 'familylabel': name, 'genderlabel': 'unknown'}
                df = pd.DataFrame([person_data])
                # ethnicity = pred_wiki_name(df, lname_col='familylabel', fname_col='givenlabel')
                ethnicity = pred_census_ln(df, 'familylabel')
                race = ethnicity.iloc[0]['race']
                # entity['ethnicity'] = race.split(",")[0]
                entity['ethnicity'] = race
                entity['gender'] = person_data['genderlabel']

                self.known_persons[name]['ethnicity'] = entity['ethnicity']
                self.known_persons[name]['gender'] = entity['gender']
        return entity

    def retrieve_geolocation(self, entity):
        name = entity['text']
        place = ''.join(filter(lambda x: x in self.printable, name))
        if len(place) > 2 and '|' not in place and place.lower() != 'None'.lower():
            if place not in self.known_locations:
                # retrieve the coordinates from OpenStreetMap
                lat, lon, country_code = self.openstreetmap.get_coordinates(place)
                if not lat == 0 or not lon == 0 or not country_code == 0:
                    self.known_locations[place] = [country_code, lat, lon]
                    entity['location'] = {
                        'lat': lat,
                        'lon': lon
                    }
                    entity['country_code'] = country_code
                else:
                    entity['calculated'] = 'Y'
            else:
                location = self.known_locations[place]
                entity['location'] = {
                    'lat': location[1],
                    'lon': location[2]
                }
                entity['country_code'] = location[0]
        return entity

    def annotate_entities(self, entities):
        annotated_entities = []
        for entity in (entity for entity in entities if 'annotated' not in entity or entity['annotated'] == 'N'):
            try:
                if entity['label'] == 'PER':
                    if 'occupation' in self.metrics and 'occupation' not in entity:
                        entity = self.retrieve_occupation(entity)
                    if 'ethnicity' in self.metrics and 'ethnicity' not in entity:
                        entity = self.retrieve_ethnicity(entity)
                if 'location' in self.metrics and entity['label'] == 'LOC':
                    if 'country_code' not in entity:
                        entity = self.retrieve_geolocation(entity)
                entity['annotated'] = 'Y'
            except (IndexError, TypeError):
                entity['annotated'] = 'Y'
            annotated_entities.append(entity)
        return annotated_entities

    def calculate_tags(self, tags):
        """
        calculates for each tag specified its representation in the selected article
        """
        df = pd.DataFrame.from_dict(tags)
        counts = df.tag.value_counts()
        result = {}
        for tag in self.spacy_tags:
            try:
                count = counts[tag]
                percentage = count / len(df)
                result[tag] = percentage
            except KeyError:
                result[tag] = 0
        return result

    def enrich_all(self):
        try:
            recommendations = self.handlers.recommendations.get_all_recommendations()
            for recommendation in recommendations:
                article = self.handlers.articles.get_by_id(recommendation.article_id)
                doc = {}
                if not article.entities:
                    _, entities, tags = self.annotator.annotate(article.text)
                else:
                    entities = article.entities
                    tags = article.tags
                enriched_entities = self.annotate_entities(entities)
                doc['entities'] = enriched_entities
                doc['tags'] = tags

                if 'length' or 'complexity' in self.metrics:
                    if not article.nsentences or not article.nwords or not article.complexity:
                        # rewrite
                        nwords, nsentences, complexity = self.textpipe.analyze(article.text)
                        doc['nwords'] = nwords
                        doc['nsentences'] = nsentences
                        doc['complexity'] = complexity
                if 'emotive' in self.metrics and not article.tag_percentages:
                    percentages = self.calculate_tags(tags)
                    doc['tag_percentages'] = percentages
                self.handlers.articles.update_doc(article.id, doc)
                self.handlers.articles.update(article.id, 'annotated', 'Y')
        except ConnectionError:
            self.save_known_entities()
            print("Connection error!")
            sys.exit()
        self.save_known_entities()



