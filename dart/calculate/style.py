import pandas as pd


class AggregateRecommendations:
    """
    Class that aggregates style metrics over users. Results are stored in a separate ES index called 'aggregated
    articles'.
    This index is used to detect per-user average number of words, sentences, complexity and popularity.
    """

    def __init__(self, handlers):
        self.handlers = handlers

    def make_dataframe(self, recommended_articles):
        """
        Retrieves all recommendations made to user_id
        Constructs a dataframe containing the relevant style metrics
        TO DO: Mock ES output and assert correct dataframe
        """
        columns = ["id", "date", "recommendation_type", "popularity", "complexity", "nwords", "nsentences"]
        table = []
        for recommendation in recommended_articles:
            article = self.handlers.articles.get_by_id(recommendation.article['id'])
            row = [article.id, recommendation.date, recommendation.type, article.popularity, article.complexity,
                   article.nwords, article.nsentences]
            table.append(row)
        df = pd.DataFrame(table, columns=columns)
        return df

    @staticmethod
    def get_averages(df):
        """
        Calculates the average value for each relevant style column.
        TO DO: Add non-happy-path doctests
        >>> df = pd.DataFrame({'complexity': [80, 70], 'popularity': [200, 400], 'nwords': [1000, 3000], 'nsentences': [20, 40]})
        >>> AggregateRecommendations.get_averages(df)
        [300.0, 75.0, 2000.0, 30.0]
        """
        avg_complexity = AggregateRecommendations.calculate_average(df, 'complexity')
        avg_popularity = AggregateRecommendations.calculate_average(df, 'popularity')
        avg_nwords = AggregateRecommendations.calculate_average(df, 'nwords')
        avg_nsentences = AggregateRecommendations.calculate_average(df, 'nsentences')
        return [avg_popularity, avg_complexity, avg_nwords, avg_nsentences]

    @staticmethod
    def calculate_average(df, column):
        """
        Calculates the average value of a column in a dataframe
        >>> df = pd.DataFrame({'Name':['Tom', 'Nick', 'Krish', 'Jack'], 'Age':[20, 21, 19, 18]})
        >>> AggregateRecommendations.calculate_average(df, 'Age')
        19.5
        """
        return df.loc[:, column].mean()

    def execute(self):
        # iterate over all recommendations generated for all users
        for user in self.handlers.users.get_all_users():
            recommended_articles = self.handlers.recommendations.get_recommendations_to_user(user.id)
            df = self.make_dataframe(recommended_articles)
            recommendation_types = df.recommendation_type.unique()
            # do for all recommendation types separately
            for recommendation_type in recommendation_types:
                articles = df[(df.recommendation_type == recommendation_type)]
                # calculate yearly averages
                averages = self.get_averages(articles)
                self.handlers.output.add_aggregated_document(
                    user.id, 'year', '31-12-2017', recommendation_type, averages)
                # calculate monthly averages
                dates = articles.date.unique()
                for date in dates:
                    articles_per_date = articles[(articles.date == date)]
                    averages = self.get_averages(articles_per_date)
                    self.handlers.output.add_aggregated_document(
                        user.id, 'month', date, recommendation_type, averages)
