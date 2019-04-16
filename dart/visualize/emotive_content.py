import pandas as pd


class IdentifyEmotiveContent:

    def __init__(self, handlers):
        self.handlers = handlers
        self.spacy_tags = ['DET', 'ADP', 'PRON']

    def calculate(self, df):
        """
        calculates for each tag specified its representation in the selected article
        """
        counts = df.tag.value_counts()
        result = {}
        for tag in self.spacy_tags:
            try:
                count = counts[tag]
                percentage = count / len(df)
                result[tag] = percentage
            except KeyError:
                result[tag] = 0
        return result

    def execute(self):
        recommendations = self.handlers.recommendations.get_all_recommendations()
        for recommendation in recommendations:
            docid = recommendation.article_id
            document = self.handlers.articles.get_by_id(docid)
            tags = document.tags
            df = pd.DataFrame.from_dict(tags)
            percentages = self.calculate(df)
            self.handlers.articles.add_field(docid, 'tag_percentages', percentages)

