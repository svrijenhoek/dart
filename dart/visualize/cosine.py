import dart.handler.NLP.cosine_similarity
import numpy as np


class CosineCalculator():

    def __init__(self, handlers):
        self.handlers = handlers

    def calculate(self, user_id, recommendation_type):
        recommendations = self.handlers.recommendations.get_recommendations_to_user(user_id, recommendation_type)
        doc_list = [recommendation.article_id for recommendation in recommendations]
        cosines = dart.handler.NLP.cosine_similarity.CosineSimilarity().calculate_cosine_similarity(doc_list)
        return np.mean(cosines)
