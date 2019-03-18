import requests
from dart.models.Recommendation import Recommendation
from dart.models.Article import Article
from dart.handler.elastic.article_handler import ArticleHandler
from dart.handler.elastic.connector import Connector
import json
import sys
import elasticsearch


known_entities = {}
searcher = ArticleHandler()
connector = Connector()

"""
This needs some serious rewriting haha
"""


def execute_query(query):
    url = 'https://query.wikidata.org/sparql'
    r = requests.get(url, params={'format': 'json', 'query': query})
    return r


def get_occupations(label):
    query = """
        SELECT DISTINCT ?occupation_label WHERE { 
          ?s ?label '""" + label + """'@nl .
          ?s wdt:P106 ?occupation .
          ?occupation rdfs:label ?occupation_label
          FILTER(LANG(?occupation_label) = "" || LANGMATCHES(LANG(?occupation_label), "nl"))
        }
        """
    r = execute_query(query)
    try:
        data = r.json()
        return [x['occupation_label']['value'] for x in data['results']['bindings']]
    except json.decoder.JSONDecodeError:
        return []


def get_party(label):
    query = """
    SELECT DISTINCT ?party_label WHERE { 
      ?s ?label '"""+label+"""'@nl .
      ?s wdt:P102 ?party .
      ?party rdfs:label ?party_label .
      FILTER(LANG(?party_label) = "" || LANGMATCHES(LANG(?party_label), "nl"))
    }
    """
    r = execute_query(query)
    try:
        data = r.json()
        return [x['party_label']['value'] for x in data['results']['bindings']]
    except json.decoder.JSONDecodeError:
        return []


def get_positions(label):
    query = """
    SELECT DISTINCT ?position_label WHERE { 
      ?s ?label '"""+label+"""'@nl .
      ?s wdt:P39 ?position .
      ?position rdfs:label ?position_label
      FILTER(LANG(?position_label) = "" || LANGMATCHES(LANG(?position_label), "nl"))
    }
    """
    r = execute_query(query)
    try:
        data = r.json()
        return [x['position_label']['value'] for x in data['results']['bindings']]
    except json.decoder.JSONDecodeError:
        return []


def update_list(o, l):
    for occupation in o:
        if occupation in l:
            l[occupation] = l[occupation]+1
        else:
            l[occupation] = 1
    return l


def add_document(doctype, user, date, doc_id, key, label, frequency):
    doc = {
        'type': doctype,
        'date': date,
        'user': user,
        'article_id': doc_id,
        key: {'name': label, 'frequency': frequency}
    }
    body = json.dumps(doc)
    try:
        connector.add_document('occupations', '_doc', body)
    except elasticsearch.exceptions.RequestError:
        print(doc)
        sys.exit()


def analyze_entity(label):
    entity_occupations = get_occupations(label)
    if 'politicus' in entity_occupations:
        entity_parties = get_party(label)
        entity_positions = get_positions(label)
    else:
        entity_parties = {}
        entity_positions = {}
    return entity_occupations, entity_parties, entity_positions


def analyze_document(doc):
    all_occupations = {}
    all_parties = {}
    all_positions = {}
    for entity in doc.entities:
        if entity['label'] == 'PER':
            name = entity['text']
            if name not in known_entities:
                entity_occupations, entity_parties, entity_positions = analyze_entity(name)
                all_occupations = update_list(entity_occupations, all_occupations)
                known_entities[name] = {'occupations': entity_occupations, 'parties': entity_parties,
                                        'positions': entity_positions}
            else:
                entry = known_entities[entity['text']]
                entity_occupations = entry['occupations']
                entity_parties = entry['parties']
                entity_positions = entry['positions']
            all_occupations = update_list(entity_occupations, all_occupations)
            all_parties = update_list(entity_parties, all_parties)
            all_positions = update_list(entity_positions, all_positions)
    return all_occupations, all_parties, all_positions


def execute():
    recommendations = [Recommendation(i) for i in searcher.get_all_documents('recommendations')]
    for recommendation in recommendations:
        print(recommendation.date)
        for recommendation_type in recommendation.get_recommendation_types():
            for docid in recommendation.recommendations[recommendation_type]:
                document = Article(searcher.get_by_docid('articles', docid))
                occupations, parties, positions = analyze_document(document)
                for occupation in occupations:
                    frequency = occupations[occupation]
                    add_document(recommendation_type, recommendation.user, recommendation.date, docid,
                                 'occupation', occupation, frequency)
                for party in parties:
                    frequency = parties[party]
                    add_document(recommendation_type, recommendation.user, recommendation.date, docid,
                                 'party', party, frequency)
                for position in positions:
                    frequency = positions[position]
                    add_document(recommendation_type, recommendation.user, recommendation.date, docid,
                                 'position', position, frequency)



