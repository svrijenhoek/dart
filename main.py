import logging
import datetime
import time
from elasticsearch import Elasticsearch

import dart.Util
import dart.populate.add_documents
import dart.populate.add_popularity
import dart.populate.simulate_users
import dart.populate.generate_recommendations
import dart.visualize.aggregate_by_user
import dart.visualize.location
import dart.visualize.occupations
import dart.visualize.personalization_old
import dart.visualize.FAT_calculations
import dart.models.Handlers
import dart.populate.enrich_articles
import dart.populate.identify_stories
import dart.handler.elastic.initialize


def main():

    logging.basicConfig(filename='dart.log', level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s')
    module_logger = logging.getLogger('main')
    elastic_connector = dart.handler.elastic.connector.ElasticsearchConnector()
    handlers = dart.models.Handlers.Handlers(elastic_connector)

    # step 0: load config file
    config = dart.Util.read_full_config_file()
    metrics = config['metrics']
    es = Elasticsearch()

    # # step 1: load articles
    # print(str(datetime.datetime.now())+"\tloading articles")
    # if es.indices.exists(index="articles") and config["append"] == "N":
    #     # delete index
    #     elastic_connector.clear_index('articles')
    #     module_logger.info("Index removed")
    # if not es.indices.exists(index="articles"):
    #     module_logger.info("Index created")
    #     dart.handler.elastic.initialize.InitializeIndex().initialize_articles()
    #     module_logger.info("Started adding documents")
    # dart.populate.add_documents.AddDocuments(config).execute()
    # # add popularity numbers from file
    # print(str(datetime.datetime.now()) + "\tadding popularity")
    # dart.populate.add_popularity.PopularityQueue().read_from_file(config['popularity_file'])
    #
    # # step 1.5: annotate reading history
    # print(str(datetime.datetime.now())+"\tenriching base articles")
    # dart.populate.enrich_articles.Enricher(handlers, config).enrich_base()

    # step 1.7: identify stories in the range specified in the configuration
    # print(str(datetime.datetime.now())+"\tidentifying stories")
    # if es.indices.exists(index="stories"):
    #     # delete index
    #     elastic_connector.clear_index('stories')
    # dart.populate.identify_stories.StoryIdentifier(handlers, config).execute()

    # step 2: simulate users
    # print(str(datetime.datetime.now())+"\tloading users")
    # if es.indices.exists(index="users") and config["append"] == "N":
    #     elastic_connector.clear_index('users')
    #     module_logger.info("User index removed")
    # module_logger.info("Simulating user data")
    # dart.populate.simulate_users.UserSimulator(config, handlers).execute()
    # time.sleep(5)
    #
    # # step 3: simulate recommendations
    # print(str(datetime.datetime.now())+"\tloading recommendations")
    # if es.indices.exists(index="recommendations") and config["append"] == "N":
    #     # delete index
    #     dart.handler.elastic.initialize.InitializeIndex().initialize_recommendations()
    #     module_logger.info("Recommendations index removed")
    # module_logger.info("Generating baseline recommendations")
    # dart.populate.generate_recommendations.RunRecommendations(config, handlers).execute()
    # time.sleep(5)

    # step 4: enrich data of recommended articles
    # print(str(datetime.datetime.now())+"\tenriching articles")
    # dart.populate.enrich_articles.Enricher(handlers, config).enrich_recommendations()

    # step 5: make visualizations
    # print(str(datetime.datetime.now())+"\taggregating data")
    # if 'length' or 'complexity' or 'popularity' or 'personalization' in metrics:
    #     module_logger.info("Visualizing user aggregations")
    #     dart.handler.elastic.initialize.InitializeIndex().initialize_aggregated()
    #     dart.visualize.aggregate_by_user.Aggregator(handlers).execute()
    # print(str(datetime.datetime.now())+"\t\tlocations")
    # if 'location' in metrics:
    #     module_logger.info("Visualizing location metrics")
    #     dart.handler.elastic.initialize.InitializeIndex().initialize_locations()
    #     dart.visualize.location.LocationVisualizer(handlers).execute()
    # print(str(datetime.datetime.now())+"\t\toccupations")
    # if 'occupation' in metrics:
    #     module_logger.info("Visualizing occupation metrics")
    #     dart.handler.elastic.initialize.InitializeIndex().initialize_occupations()
    #     dart.visualize.occupations.OccupationCalculator(handlers).execute()

    # TO DO: ethnicity, source, emotive
    print(str(datetime.datetime.now()) + "\tFAT calculations")
    dart.visualize.FAT_calculations.FATCalculator(handlers, config).execute()


if __name__ == "__main__":
    main()
