import datetime

import dart.Util
import dart.metrics.start_calculations
import dart.models.Handlers
import dart.handler.mongo.connector


def main():
    elastic_connector = dart.handler.elastic.connector.ElasticsearchConnector()
    mongo_connector = dart.handler.mongo.connector.MongoConnector()
    handlers = dart.models.Handlers.Handlers(elastic_connector, mongo_connector)

    # step 0: load config file
    config = dart.Util.read_full_config_file()

    print(str(datetime.datetime.now()) + "\tMetrics")
    dart.metrics.start_calculations.MetricsCalculator(handlers, config).execute()


if __name__ == "__main__":
    main()
