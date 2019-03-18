import logging
from elasticsearch import Elasticsearch

import dart.Util
import dart.populate.add_documents
import dart.populate.simulate_users
import dart.populate.generate_recommendations
import dart.calculate.style
import dart.calculate.location
import dart.calculate.occupations
import dart.calculate.personalization
import dart.handler.elastic.connector

logging.basicConfig(filename='dart.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s')
module_logger = logging.getLogger('main')
# print(logging.getLoggerClass().root.handlers[0].baseFilename)
elastic_connector = dart.handler.elastic.connector.Connector()

# step 0: load config file
config = dart.Util.read_full_config_file()
es = Elasticsearch()

# step 1: load articles
if es.indices.exists(index="articles") and config["append"] == "N":
    # delete index
    elastic_connector.clear_index('articles')
    module_logger.info("Index removed")
    # initialization is currently not necessary for articles
if not es.indices.exists(index="articles"):
    # placeholder in case this is going to be needed
    module_logger.info("Index created")


if config['articles_schema'] == "N":
    module_logger.info("Started adding documents")
    temp = dart.populate.add_documents.AddDocuments(config['articles_folder'])
    temp.execute()
else:
    module_logger.info("Schema interpretation to be implemented")

# step 2: simulate users
if es.indices.exists(index="users") and config["append"] == "N":
    # delete index
    elastic_connector.clear_index('users')
    module_logger.info("User index removed")
    # initialization is currently not necessary for articles
if config['user_load'] == "Y":
    module_logger.warning("Loading user data to be implemented")
else:
    module_logger.info("Simulating user data")
    dart.populate.simulate_users.execute(config)

# step 3: simulate recommendations
if es.indices.exists(index="recommendations") and config["append"] == "N":
    # delete index
    elastic_connector.clear_index('recommendations')
    module_logger.info("Recommendations index removed")
    # initialization is currently not necessary for articles
if config['recommendations_load'] == 'Y':
    module_logger.warning("Loading recommendation data to be implemented")
if not config['recommendations_baseline'] == []:
    module_logger.info("Generating baseline recommendations")
    dart.populate.generate_recommendations.execute(config)

# step 4: do analyses
metrics = config['metrics']
if 'length' or 'complexity' or 'popularity' in metrics:
    module_logger.info("Calculating style metrics")
    dart.calculate.style.execute()
if 'personalization' in metrics:
    module_logger.info("Calculating personalization metrics")
    dart.calculate.personalization.execute()
if 'locations' in metrics:
    module_logger.info("Calculating location metrics")
    dart.calculate.location.execute()
if 'occupations' in metrics:
    module_logger.info("Calculating occupation metrics")
    dart.calculate.occupations.execute()
