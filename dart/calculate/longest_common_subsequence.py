import urllib

base = 'https://query.wikidata.org/sparql?query='

query = """
        SELECT DISTINCT ?party_label ?label where {
          ?person wdt:P106 wd:Q82955 .
          ?person wdt:P27  wd:Q29999 .
          ?person wdt:P102 ?party .
          ?party rdfs:label ?party_label .
          ?person rdfs:label ?label .
          FILTER(LANG(?label) = "" || LANGMATCHES(LANG(?label), "nl")) .
          FILTER(LANG(?party_label) = "" || LANGMATCHES(LANG(?party_label), "nl"))
        } 
        ORDER BY ?party_label ?label
        LIMIT 10000
"""
