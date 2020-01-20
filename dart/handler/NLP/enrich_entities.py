import dart.Util
import dart.handler.other.wikidata
import dart.handler.other.openstreetmap
import string
from collections import defaultdict
import pandas as pd


class EntityEnricher:

    def __init__(self, metrics, language, politics):
        self.metrics = metrics
        self.language = language
        self.openstreetmap = dart.handler.other.openstreetmap.OpenStreetMap()
        self.wikidata = dart.handler.other.wikidata.WikidataHandler(self.language)
        self.printable = set(string.printable)
        self.political_data = pd.DataFrame(politics)

        try:
            self.known_locations = dart.Util.read_json_file('output/known_locations.json')
        except FileNotFoundError:  # when no location file is found, create a new dict
            self.known_locations = {}
        try:
            self.known_persons = dart.Util.read_json_file('output/known_persons.json')
        except FileNotFoundError:  # when no persons file is found, create a new dict
            self.known_persons = {}
        try:
            self.unknown_persons = defaultdict(int, dart.Util.read_json_file('output/unknown_persons.json'))
        except FileNotFoundError:  # when no persons file is found, create a new dict
            self.unknown_persons = defaultdict(int)
        try:
            self.known_organizations = dart.Util.read_json_file('output/known_organizations.json')
        except FileNotFoundError:  # when no organization file is found, create a new dict
            self.known_organizations = {}

    def known(self, name, alternative, listtype):
        if listtype == 'person': known_list = self.known_persons
        elif listtype == 'organization': known_list = self.known_organizations
        elif listtype == 'location': known_list = self.known_locations

        # situation 1: name is directly known
        if name in known_list:
            known_list[name]['alternative'] = list(set(alternative + known_list[name]['alternative']))
            return known_list[name]
        # situation 2: one of the alternative names is directly in dict
        for alt in alternative:
            if not (listtype == 'person' and (name.startswith(alt) and " " not in alt)):
                if alt in known_list:
                    known_list[alt]['alternative'] = list(set(alternative + known_list[alt]['alternative']))
                    return known_list[alt]
        # situation 3: name is a known alternative
        for k, v in known_list.items():
            if name in v['alternative']:
                known_list[k]['alternative'] = list(set(alternative + known_list[k]['alternative']))
                return v
            # situation 4: shared alternative names
            # this does not work for first names only!
            # elif len(list(set(alternative) & set(v['alternative']))) > 0:
            #    known_list[k]['alternative'] = list(set(alternative + known_list[k]['alternative']))
            #    return v
        return

    def enrich(self, entity):
        if entity['label'] == 'PER':
            if 'occupation' in self.metrics and 'occupation' not in entity:
                entity = self.retrieve_person_data(entity)
            # if 'ethnicity' in self.metrics and 'ethnicity' not in entity:
            #     entity = self.retrieve_ethnicity(entity)
        if 'location' in self.metrics and entity['label'] == 'LOC':
            if 'country_code' not in entity:
                entity = self.retrieve_geolocation(entity)
        if 'organization' in self.metrics and entity['label'] == 'ORG':
            if 'type' not in entity:
                entity = self.retrieve_company_data(entity)
        entity['annotated'] = 'Y'
        return entity

    def retrieve_person_data(self, entity):
        """
        Function that first aims to see if the entity is already known. If not, it retrieves data from Wikipedia.
        """
        name = entity['text']
        # see if the entity is already known
        known_entry = self.known(name, entity['alternative'], 'person')
        # if it is unknown, or we don't gave any additional data about it, try to find it again
        # reasoning here is that we may have encountered another way of spelling the entity's name that would be found
        if not known_entry or 'givenname' not in known_entry or known_entry['givenname'] == []:
            # if the entity is already known, but we just don't have additional data about it, try if we can find
            # information with a different way of spelling
            if known_entry:
                found, data = self.wikidata.get_person_data(name, known_entry['alternative'])
                alternative = {'alternative': list(set(known_entry['alternative'] +
                                                                     entity['alternative']))}
                # if a new way of spelling is found, delete the old entry
                if found != name and name in self.known_persons:
                    del self.known_persons[name]
            # if this is an entirely new entry
            else:
                found, data = self.wikidata.get_person_data(name, entity['alternative'])
                alternative = {'alternative': entity['alternative']}
                if 'politician' in data['occupation']:
                    data = self.resolve_politicians(found, data)
            # update the list with the information that was found
            try:
                if data:
                    self.known_persons[found] = alternative
                    for k, v in data.items():
                        self.known_persons[found][k] = v
                        entity[k] = v
                else:
                    self.unknown_persons[name] += 1
            except AttributeError as e:
                print(e)
                print(data)
            except KeyError:
                print(name)
                print(known_entry)
                print(found)
        else:
            for k, v in known_entry.items():
                entity[k] = v
        return entity

    def resolve_politicians(self, name, data):
        df = self.political_data
        row = df.loc[df['name'] == name]
        if not row.empty and not row.end_date:
            data['current_party'] = row.group
        return data

    def retrieve_geolocation(self, entity):
        name = entity['text']
        place = ''.join(filter(lambda x: x in self.printable, name))
        place = place.replace('\n', '').replace('\r', '')
        if len(place) > 2 and '|' not in place and place.lower() != 'None'.lower():
            known_entry = self.known(name, entity['alternative'], 'location')
            if known_entry:
                location = known_entry
                entity['location'] = {
                    'lat': location['lat'],
                    'lon': location['lon']
                }
                entity['country_code'] = location['country_code']
            else:
                try:
                    # retrieve the coordinates from OpenStreetMap
                    try:
                        lat, lon, country_code = self.openstreetmap.get_coordinates(place)
                        if not lat == 0 or not lon == 0 or not country_code == 0:
                            self.known_locations[place] = {'country_code': country_code, 'lat': lat, 'lon': lon,
                                                           'alternative': entity['alternative']}
                            entity['location'] = {
                                'lat': lat,
                                'lon': lon
                            }
                            entity['country_code'] = country_code
                        else:
                            entity['calculated'] = 'Y'
                    except TypeError:
                        pass
                except IndexError:
                    entity['calculated'] = 'Y'
        return entity

    def retrieve_company_data(self, entity):
        name = entity['text']
        known_entry = self.known(name, entity['alternative'], 'organization')
        if known_entry:
            entity['industry'] = known_entry['industry']
            entity['instance'] = known_entry['instance']
            entity['country'] = known_entry['country']
            return entity
        else:
            # for now we see if we can work with only the first result
            # problem with this approach: if one field is not filled, they all fail!!
            response = self.wikidata.get_company_data(name)
            try:
                industry = response['industry']
                instance = response['instance']
                country = response['country']

                self.known_organizations[name] = {'industry': industry, 'instance': instance, 'country': country, 'alternative': entity['alternative']}
                entity['industry'] = industry
                entity['instance'] = instance
                entity['country'] = country
            except TypeError:
                pass
        return entity

    def save(self):
        dart.Util.write_to_json('output/known_locations.json', self.known_locations)
        dart.Util.write_to_json('output/known_persons.json', self.known_persons)
        dart.Util.write_to_json('output/unknown_persons.json', self.unknown_persons)
        dart.Util.write_to_json('output/known_organizations.json', self.known_organizations)
