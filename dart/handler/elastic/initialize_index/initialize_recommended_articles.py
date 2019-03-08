from elasticsearch import Elasticsearch

es = Elasticsearch()
mapping = {
  "mappings": {
    "_doc": {
      "properties": {
        "recommendation.date": {
          "type": "date",
          "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis||dd-MM-YYYY"
        },
        "article.date": {
          "type": "date"
        },
        "article.text": {
          "type": "text",
          "term_vector": "with_positions_offsets",
          "analyzer": "dutch"
        },
        "article.title": {
          "type": "text",
          "term_vector": "with_positions_offsets",
          "analyzer": "dutch"
        },
        "article.style.complexity": {
          "type": "integer"
        },
        "article.style.nsentences": {
          "type": "integer"
        },
        "article.style.nwords": {
          "type": "integer"
        },
      }
    }
  }
}
es.indices.delete(index='recommended_articles')
print("Index removed")
es.indices.create(index='recommended_articles', body=mapping)
print("Index created")
