import requests
import json
import time


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
        r = requests.get(self.url, params={'format': 'json', 'query': query})
        return r

    @staticmethod
    def read_response(response, label):
        try:
            data = response.json()
            return [x[label]['value'] for x in data['results']['bindings']]
        except json.decoder.JSONDecodeError:
            return []

    @staticmethod
    def read_response_list(response):
        try:
            data = response.json()
            entry = data['results']['bindings'][0]
            try:
                givenname = entry['givenlabel']['value']
            except IndexError:
                givenname = ''
            try:
                familylabel = entry['familylabel']['value']
            except IndexError:
                familylabel = ''
            try:
                genderlabel = entry['genderlabel']['value']
            except IndexError:
                genderlabel = ''

            return {'givenlabel': givenname, 'familylabel': familylabel, 'genderlabel': genderlabel}
        except json.decoder.JSONDecodeError:
            return []
        except IndexError:
            return []

    def get_occupations(self, label):
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

    def get_person_data(self, label):
        query = """
            SELECT DISTINCT ?givenlabel ?familylabel ?genderlabel where {
              ?person rdfs:label '"""+label+"""'@nl .
              OPTIONAL{?person wdt:P734 ?familyname .
                      ?familyname rdfs:label ?familylabel .}
              OPTIONAL{?person wdt:P735  ?givenname .
                      ?givenname rdfs:label ?givenlabel .}
              OPTIONAL{?person wdt:P21 ?gender .
                      ?gender rdfs:label ?genderlabel}
              FILTER(LANG(?genderlabel) = "" || LANGMATCHES(LANG(?genderlabel), "en"))
              FILTER(LANG(?givenlabel) = "" || LANGMATCHES(LANG(?givenlabel), "nl"))
              FILTER(LANG(?familylabel) = "" || LANGMATCHES(LANG(?familylabel), "en"))
            } 
            ORDER BY ?familyname
            LIMIT 1
        """
        r = self.execute_query(query)
        return self.read_response_list(r)
