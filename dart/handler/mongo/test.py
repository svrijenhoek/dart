import dart.handler.NLP.enrich_entities
import dart.models.Handlers
import dart.handler.mongo.connector
import dart.handler.elastic.connector

entity = {
  "start_char": 16,
  "end_char": 20,
  "text": "Angela Merkel",
  "label": "PER",
  "alternative": []
}

elastic_connector = dart.handler.elastic.connector.ElasticsearchConnector()
mongo_connector = dart.handler.mongo.connector.MongoConnector()
handlers = dart.models.Handlers.Handlers(elastic_connector, mongo_connector)
enricher = dart.handler.NLP.enrich_entities.EntityEnricher([], "German", [], handlers)
entity = enricher.enrich(entity)
print(entity)
