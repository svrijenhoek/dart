class Style:

    def __init__(self, handlers):
        self.handlers = handlers

    @staticmethod
    def average(numbers):
        try:
            if sum(numbers) == 0:
                return 0
            else:
                return sum(numbers)/len(numbers)
        except TypeError:
            return 0

    def get_metrics(self, user_id, recommendation_type):
        recommendations = self.handlers.recommendations.get_recommendations_to_user(user_id, recommendation_type)
        popularity = []
        nwords = []
        nsentences = []
        complexity = []
        tags = {}
        for recommendation in recommendations:
            article = self.handlers.articles.get_by_id(recommendation.article_id)
            nwords.append(article.nwords)
            nsentences.append(article.nsentences)
            complexity.append(article.complexity)
            popularity.append(article.popularity)
            for tag in article.tag_percentages:
                if tag in tags:
                    tags[tag].append(article.tag_percentages[tag])
                else:
                    tags[tag] = [article.tag_percentages[tag]]
        pos_averages = {}
        for tag in tags:
            pos_averages[tag] = Style.average(tags[tag])
        return [Style.average(popularity), Style.average(complexity), Style.average(nwords), Style.average(nsentences),
                pos_averages]
