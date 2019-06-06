import dart.Util
import dart.handler.other.wikidata
import dart.handler.other.openstreetmap
import string
import pandas as pd
from ethnicolr import pred_census_ln


class EntityEnricher:

    def __init__(self, metrics):
        self.metrics = metrics
        self.openstreetmap = dart.handler.other.openstreetmap.OpenStreetMap()
        self.wikidata = dart.handler.other.wikidata.WikidataHandler()
        self.printable = set(string.printable)

        try:
            self.known_locations = dart.Util.read_json_file('output/known_locations.json')
        except FileNotFoundError:
            self.known_locations = {}
        try:
            self.known_persons = dart.Util.read_json_file('output/known_persons.json')
        except FileNotFoundError:
            self.known_persons = {}
        try:
            self.known_organizations = dart.Util.read_json_file('output/known_organizations.json')
        except FileNotFoundError:
            self.known_organizations = {}

    def enrich(self, entity):
        try:
            if entity['label'] == 'PER':
                if 'occupation' in self.metrics and 'occupation' not in entity:
                    entity = self.retrieve_occupation(entity)
                if 'ethnicity' in self.metrics and 'ethnicity' not in entity:
                    entity = self.retrieve_ethnicity(entity)
            if 'location' in self.metrics and entity['label'] == 'LOC':
                if 'country_code' not in entity:
                    entity = self.retrieve_geolocation(entity)
            if 'organization' in self.metrics and entity['label'] == 'ORG':
                if 'type' not in entity:
                    entity = self.retrieve_company_data(entity)
            entity['annotated'] = 'Y'
        except (IndexError, TypeError):
            entity['annotated'] = 'Y'
            return entity
        return entity

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

    def retrieve_company_data(self, entity):
        name = entity['text']
        try:
            entity['industry'] = self.known_organizations[name]['industry']
            entity['instance'] = self.known_organizations[name]['instance']
            entity['country'] = self.known_organizations[name]['country']
        except KeyError:
            # for now we see if we can work with only the first result
            company_data = self.wikidata.get_company_data(name)[0]
            self.known_organizations[name] = {}
            entity['industry'] = company_data['industry']
            self.known_organizations[name]['industry'] = entity['industry']
            entity['instance'] = company_data['instance']
            self.known_organizations[name]['instance'] = entity['instance']
            entity['country'] = company_data['country']
            self.known_organizations[name]['country'] = entity['country']
        return entity

    def save(self):
        dart.Util.write_to_json('output/known_locations.json', self.known_locations)
        dart.Util.write_to_json('output/known_persons.json', self.known_persons)
        dart.Util.write_to_json('output/known_organizations.json', self.known_organizations)
