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
        r = requests.get(self.url, params={'format': 'json', 'query': query})
        return r

    @staticmethod
    def read_response(response, label):
        try:
            data = response.json()
            return [x[label]['value'] for x in data['results']['bindings']]
        except json.decoder.JSONDecodeError:
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
