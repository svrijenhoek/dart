from collections import Counter

class LocationVisualizer:

    def __init__(self, handlers):
        self.handlers = handlers

    def execute(self):
        recommendations = self.handlers.recommendations.get_all_recommendations()
        result = {}
        count = 0
        for recommendation in recommendations:
            count += 1
            for docid in recommendation.articles:
                document = self.handlers.articles.get_by_id(docid)
                entities = document.entities
                for entity in entities:
                    if entity['label'] == 'LOC':
                        try:
                            if not entity['location']['lat'] == 0 and not entity['location']['lon'] == 0:
                                if recommendation.type not in result:
                                    result[recommendation.type] = Counter()
                                result[recommendation.type][entity['country_code']] += 1
                                # location = [entity['text'], [entity['country_code'], entity['location']]]
                                # self.handlers.output.add_location_document(document.publication_date,
                                #                                           recommendation.type, location)
                        except KeyError:
                            pass
            if count % 1000 == 0:
                print(count)
        for recommendation_type in result:
            for country in result[recommendation_type]:
                frequency = result[recommendation_type][country]
                self.handlers.output.add_location_document(recommendation_type, country, frequency)

