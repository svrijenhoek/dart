import dart.visualize.style
import dart.visualize.personalization_old
import dart.visualize.cosine


class Aggregator:
    """
    Class that aggregates style metrics over users. Results are stored in a separate ES index called 'aggregated
    articles'.
    This index is used to detect per-user average number of words, sentences, complexity and popularity.
    """

    def __init__(self, handlers, config):
        self.handlers = handlers
        self.config = config
        self.style_calculator = dart.visualize.style.Style(handlers)
        self.personalization_calculator = dart.visualize.personalization_old.Personalization(handlers)
        self.cosine_calculator= dart.visualize.cosine.CosineCalculator(handlers, config['language'])

    def aggregate_per_user(self, recommendation_type):
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

    def aggregate_per_recommender(self, recommendation_type):
        recommendations = self.handlers.recommendations.get_recommendations_of_type(recommendation_type)
        style = self.style_calculator.get_metrics(recommendations)
        # classification = self.classification_calculator.get_average(recommendations)
        # spread = self.spread_calculator.get_coverage(recommendations)
        if not style == [0, 0, 0, 0, {}]:
            self.handlers.output.add_aggregated_per_recommender(recommendation_type,
                                                                style)

    def execute(self):
        # iterate over all recommendations generated for all users
        types = self.handlers.recommendations.get_recommendation_types()
        for recommendation_type in types:
            self.aggregate_per_user(recommendation_type)
            # self.aggregate_per_recommender(recommendation_type)
