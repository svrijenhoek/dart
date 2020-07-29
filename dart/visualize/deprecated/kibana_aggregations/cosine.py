import dart.handler.NLP.cosine_similarity


class CosineCalculator:

    def __init__(self, handlers, language):
        self.handlers = handlers
        self.language = language

    def calculate(self, user_id, recommendation_type):
        recommendations = self.handlers.recommendations.get_recommendations_to_user(user_id, recommendation_type)
        doc_list = []
        for recommendation in recommendations:
            for article_id in recommendation.articles:
                doc_list.append(article_id)
        mean_cosine = dart.handler.NLP.cosine_similarity.CosineSimilarity(self.language).calculate_all(doc_list)
        return mean_cosine
