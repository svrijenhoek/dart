from elasticsearch import Elasticsearch

es = Elasticsearch()
mapping = {
  "mappings": {
    "_doc": {
      "properties": {
        "date": {
          "type": "date"
        },
        "location": {
          "type": "geo_point"
        },
      }
    }
  }
}
es.indices.delete(index='locations')
print("Index removed")
es.indices.create(index='locations', body=mapping)
print("Index created")
