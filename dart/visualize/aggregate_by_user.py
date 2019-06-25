import dart.visualize.style
import dart.visualize.personalization
import dart.visualize.cosine


class AggregateRecommendations:
    """
    Class that aggregates style metrics over users. Results are stored in a separate ES index called 'aggregated
    articles'.
    This index is used to detect per-user average number of words, sentences, complexity and popularity.
    """

    def __init__(self, handlers):
        self.handlers = handlers
        self.style_calculator = dart.visualize.style.Style(handlers)
        self.personalization_calculator = dart.visualize.personalization.Personalization(handlers)
        self.cosine_calculator= dart.visualize.cosine.CosineCalculator(handlers)

    def execute(self):
        # iterate over all recommendations generated for all users
        types = self.handlers.recommendations.get_recommendation_types()
        for recommendation_type in types:
            for user in self.handlers.users.get_all_users():
                recommendations = self.handlers.recommendations.get_recommendations_to_user(user.id, recommendation_type)
                style = self.style_calculator.get_metrics(recommendations)
                personalization = self.personalization_calculator.get_personalization(user.id, recommendation_type)
                cosine = self.cosine_calculator.calculate(user.id, recommendation_type)
                if not style == [0, 0, 0, 0, {}]:
                    self.handlers.output.add_aggregated_document(user.id,
                                                                 recommendation_type,
                                                                 style,
                                                                 personalization,
                                                                 cosine)
