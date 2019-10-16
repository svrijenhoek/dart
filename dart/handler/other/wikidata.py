import requests
import json


class WikidataHandler:
    """
    Class that constructs Wikidata queries, executes them and reads responses
    """

    def __init__(self):
        self.url = 'https://query.wikidata.org/sparql'

    def execute_query(self, query):
        """
        Sends a SPARQL query to Wikidata.
        TO DO: Write tests
        """
        try:
            r = requests.get(self.url, params={'format': 'json', 'query': query})
            return r
        except (ConnectionAbortedError, ConnectionError):
            return ConnectionError

    @staticmethod
    def read_response(response, label):
        try:
            data = response.json()
            return [x[label]['value'] for x in data['results']['bindings']]
        except json.decoder.JSONDecodeError:
            return []

    @staticmethod
    def read_person_response_list(response):
        try:
            data = response.json()
            givenname = list(set([x['givenname']['value'] for x in data['results']['bindings'] if 'givenname' in x]))
            familyname = list(set([x['familyname']['value'] for x in data['results']['bindings'] if 'family' in x]))
            occupations = list(set([x['occupations']['value'] for x in data['results']['bindings'] if 'occupations' in x]))
            party = list(set([x['party']['value'] for x in data['results']['bindings'] if 'party' in x]))
            positions = list(set([x['position']['value'] for x in data['results']['bindings'] if 'position' in x]))
            gender = list(set([x['gender']['value'] for x in data['results']['bindings'] if 'gender' in x]))
            citizen = list(set([x['citizen']['value'] for x in data['results']['bindings'] if 'citizen' in x]))
            ethnicity = list(set([x['ethnicity']['value'] for x in data['results']['bindings'] if 'ethnicity' in x]))
            sexuality = list(set([x['sexuality']['value'] for x in data['results']['bindings'] if 'sexuality' in x]))

            return {'givenname': givenname, 'familyname': familyname, 'gender': gender, 'occupations': occupations,
                    'party': party, 'positions': positions, 'citizen': citizen, 'ethnicity': ethnicity,
                    'sexuality': sexuality}
        except json.decoder.JSONDecodeError:
            return []
        except IndexError:
            return []

    @staticmethod
    def read_company_response_list(response):
        try:
            data = response.json()
            output = []
            for entry in data['results']['bindings']:
                try:
                    industry = entry['industryLabel']['value']
                except KeyError:
                    industry = ''
                try:
                    instance = entry['instanceLabel']['value']
                except KeyError:
                    instance = ''
                try:
                    country = entry['countryLabel']['value']
                except KeyError:
                    country = ''
                output.append({'industry': industry, 'instance': instance, 'country': country})
            return output
        except json.decoder.JSONDecodeError:
            return []
        except IndexError:
            return []

    def get_person_data(self, label, alternatives):
        response = self.person_data_query(label)
        if response and (response['givenname'] or response['gender'] or response['citizen']):
            return label, response
        else:
            for alternative in alternatives:
                response = self.person_data_query(alternative)
                if response and (response['givenname'] or response['gender'] or response['citizen']):
                    return alternative, response
        return label, {}

    def occupations_query(self, label):
        """
        Returns a list of occupations known on Wikidata for a named entity of type PER.
        When no occupation can be found an empty list is returned.
        """
        query = """
            SELECT DISTINCT ?occupation_label WHERE { 
                ?s ?label '""" + label + """'@nl .
                ?s wdt:P106 ?occupation .
                ?occupation rdfs:label ?occupation_label
                FILTER(LANG(?occupation_label) = "" || LANGMATCHES(LANG(?occupation_label), "nl"))
            }
            """
        r = self.execute_query(query)
        return self.read_response(r, 'occupation_label')

    def get_party(self, label):
        query = """
            SELECT DISTINCT ?party_label WHERE { 
              ?s ?label '""" + label + """'@nl .
              ?s wdt:P102 ?party .
              ?party rdfs:label ?party_label .
              FILTER(LANG(?party_label) = "" || LANGMATCHES(LANG(?party_label), "nl"))
            }
            """
        r = self.execute_query(query)
        return self.read_response(r, 'party_label')

    def get_positions(self, label):
        query = """
            SELECT DISTINCT ?position_label WHERE { 
              ?s ?label '""" + label + """'@nl .
              ?s wdt:P39 ?position .
              ?position rdfs:label ?position_label
              FILTER(LANG(?position_label) = "" || LANGMATCHES(LANG(?position_label), "nl"))
            }
            """
        r = self.execute_query(query)
        return self.read_response(r, 'position_label')

    def person_data_query(self, label):
        try:
            query = """
                SELECT DISTINCT ?givenname ?familyname ?occupations ?party ?position ?gender ?citizen ?ethnicity ?sexuality WHERE { 
                ?s ?label '"""+label+"""' .
              OPTIONAL {
                ?s wdt:P735 ?a . 
                ?a rdfs:label ?givenname .
                FILTER(LANG(?givenname) = "" || LANGMATCHES(LANG(?givenname), "nl"))
              }
              OPTIONAL {
                ?s wdt:P734 ?b . 
                ?b rdfs:label ?familyname .
                FILTER(LANG(?familyname) = "" || LANGMATCHES(LANG(?familyname), "nl"))
              }
              OPTIONAL {
                ?s wdt:P106 ?c .
                ?c rdfs:label ?occupations .
                FILTER(LANG(?occupations) = "" || LANGMATCHES(LANG(?occupations), "nl"))
              }
              OPTIONAL {
                ?s wdt:P102 ?d .
                ?d rdfs:label ?party .
                FILTER(LANG(?party) = "" || LANGMATCHES(LANG(?party), "nl"))
              }
              OPTIONAL {
                ?s wdt:P39 ?e .
                ?e rdfs:label ?position .
                FILTER(LANG(?position) = "" || LANGMATCHES(LANG(?position), "nl"))
              }
              OPTIONAL {
                ?s wdt:P21 ?f .
                ?f rdfs:label ?gender .
                FILTER(LANG(?gender) = "" || LANGMATCHES(LANG(?gender), "nl"))
              }
              OPTIONAL {
                   ?s wdt:P172 ?g . 
                   ?g rdfs:label ?ethnicity .
                   FILTER(LANG(?ethnicity) = "" || LANGMATCHES(LANG(?ethnicity), "nl"))
                }
              OPTIONAL {
                ?s wdt:P27 ?h .
                ?h rdfs:label ?citizen
                FILTER(LANG(?citizen) = "" || LANGMATCHES(LANG(?citizen), "nl"))
                }
               OPTIONAL {
                ?s wdt:P91 ?i .
                ?i rdfs:label ?sexuality
                FILTER(LANG(?sexuality) = "" || LANGMATCHES(LANG(?sexuality), "nl"))
                }
            }"""
            r = self.execute_query(query)
            return self.read_person_response_list(r)
        except ConnectionAbortedError:
            return []

    def get_company_data(self, label):
        try:
            query = """
            SELECT DISTINCT ?instanceLabel ?industryLabel ?countryLabel WHERE { 
                ?s rdfs:label '"""+label+"""'@nl .
                ?s wdt:P571 ?inception .
                OPTIONAL {?s wdt:P31 ?instance . }
                OPTIONAL {?s wdt:P452 ?industry . }
                OPTIONAL {?s wdt:P17 ?country }
                SERVICE wikibase:label { bd:serviceParam wikibase:language "nl". }
            }            
            """
            r = self.execute_query(query)
            return self.read_company_response_list(r)
        except ConnectionAbortedError:
            return []
