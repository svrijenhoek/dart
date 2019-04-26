import string
from ethnicolr import pred_wiki_name
import pandas as pd

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
        self.spacy_tags = ['DET', 'ADP', 'PRON']

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
                ethnicity = pred_wiki_name(df, lname_col='familylabel', fname_col='givenlabel')
                race = ethnicity.iloc[0]['race']
                entity['ethnicity'] = race.split(",")[-1]
                entity['gender'] = person_data['genderlabel']

                self.known_persons[name]['ethnicity'] = entity['ethnicity']
                self.known_persons[name]['gender'] = entity['gender']
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
                if 'occupation' not in entity:
                    entity = self.retrieve_occupation(entity)
                if 'ethnicity' not in entity:
                    entity = self.retrieve_ethnicity(entity)
            if entity['label'] == 'LOC':
                if 'country_code' not in entity:
                    entity = self.retrieve_geolocation(entity)
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
        recommendations = self.handlers.recommendations.get_all_recommendations()
        for recommendation in recommendations:
            article = self.handlers.articles.get_by_id(recommendation.article_id)
            print(article.title)
            if article.annotated == 'N':
                doc = {}
                if not article.entities:
                    _, entities, tags = self.annotator.annotate(article.text)
                else:
                    entities = article.entities
                    tags = article.tags
                enriched_entities = self.annotate_entities(entities)
                doc['entities'] = enriched_entities
                doc['tags'] = tags
                if not article.nsentences or not article.nwords or not article.complexity:
                    # rewrite
                    nwords, nsentences, complexity = self.textpipe.analyze(article.text)
                    doc['nwords'] = nwords
                    doc['nsentences'] = nsentences
                    doc['complexity'] = complexity
                if not article.tag_percentages:
                    percentages = self.calculate_tags(tags)
                    doc['tag_percentages'] = percentages
                self.handlers.articles.update_doc(article.id, doc)
                self.handlers.articles.update(article.id, 'annotated', 'Y')
        self.save_known_entities()



