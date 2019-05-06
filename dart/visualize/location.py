class LocationVisualizer:

    def __init__(self, handlers):
        self.handlers = handlers

    def execute(self):
        recommendations = self.handlers.recommendations.get_all_recommendations()
        for recommendation in recommendations:
            docid = recommendation.article_id
            document = self.handlers.articles.get_by_id(docid)
            entities = document.entities
            for entity in entities:
                if entity['label'] == 'LOC':
                    try:
                        if not entity['location']['lat'] == 0 and not entity['location']['lon'] == 0:
                            location = [entity['text'], [entity['country_code'], entity['location']]]
                            self.handlers.output.add_location_document(document.publication_date,
                                                                       recommendation.type, location)
                    except KeyError:
                        pass


