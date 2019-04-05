import dart.visualize.style
import dart.visualize.personalization


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

    def execute(self):
        # iterate over all recommendations generated for all users
        for recommendation_type in self.handlers.recommendations.get_recommendation_types():
            for user in self.handlers.users.get_all_users():
                style = self.style_calculator.get_metrics(user.id, recommendation_type)
                personalization = self.personalization_calculator.get_personalization(user.id, recommendation_type)
                self.handlers.output.add_aggregated_document(user.id, recommendation_type, style, personalization)
