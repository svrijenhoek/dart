import sys
import itertools
import pandas as pd
from dart.handler.elastic.article_handler import ArticleHandler
from dart.models.Article import Article
from dart.models.Recommendation import Recommendation
import dart.Util as Util


class NetworkAnalysis:

    def __init__(self):
        self.searcher = ArticleHandler()
        self.results = []

    @staticmethod
    def compare_entities(df1, df2):
        s2 = pd.DataFrame()
        df1_per = df1[(df1.label == 'PER')]
        df2_per = df2[(df2.label == 'PER')]
        if len(df1_per) > 0 and len(df2_per) > 0:
            s1 = pd.merge(df1_per, df2_per, how='inner', on=['text'])
            s2 = s1.drop_duplicates(subset='text')
        return len(s2)

    def add_to_results(self, id1, id2, weight):
        self.results.append(
            {
                'source': id1,
                'target': id2,
                'weight': weight
            }
        )

    def compare_documents(self, documents):
        for a, b in itertools.combinations(documents, 2):
            try:
                df1 = pd.DataFrame.from_dict(a.entities)
                df2 = pd.DataFrame.from_dict(b.entities)
                links = self.compare_entities(df1, df2)
                if links > 0:
                    self.add_to_results(a.id, b.id, links)
            except AttributeError:
                continue

    def get_recommendations(self):
        table = []
        # get all unique users in the dataset
        recommendations = [Recommendation(i) for i in self.searcher.get_all_documents('recommendations')]
        for rec in recommendations:
            date = rec.date
            user_id = rec.user
            for recommendation_type in rec.get_recommendation_types():
                for docid in rec.get_articles_for_type(recommendation_type):
                    table.append([user_id, date, recommendation_type, docid])
        return pd.DataFrame(table, columns=['user_id', 'date', 'type', 'docid'])

    def execute(self):
        df = self.get_recommendations()
        for user_id in df.user_id.unique():
            user_df = df[(df.user_id == user_id)]
            for recommendation_type in user_df.type.unique():
                self.results = []
                user_type_df = user_df[(user_df.type == recommendation_type)]
                documents = [Article(self.searcher.get_by_docid('articles', doc)) for doc in user_type_df.docid.unique()]
                self.compare_documents(documents)
                Util.write_to_json('..\..\output\graph\\result_'+user_id+'_'+recommendation_type+'.json', self.results)
            print('{} finished'.format(user_id))


def main(argv):
    calculations = NetworkAnalysis()
    calculations.execute()


if __name__ == "__main__":
    main(sys.argv[1:])
