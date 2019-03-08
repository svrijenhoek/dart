from elasticsearch import Elasticsearch

es = Elasticsearch()
mapping = {
  "mappings": {
    "_doc": {
      "properties": {
        "date": {
          "type": "date",
          "format": "dd-MM-YYYY"
        },
        "avg_complexity": {
          "type": "double"
        },
        "avg_popularity": {
          "type": "double"
        },
        "avg_nwords": {
          "type": "double"
        },
        "avg_nsentences": {
          "type": "double"
        },
      }
    }
  }
}
es.indices.delete(index='aggregated_recommendations')
print("Index removed")
es.indices.create(index='aggregated_recommendations', body=mapping)
print("Index created")
