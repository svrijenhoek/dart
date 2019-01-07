import sys
from dart.helper.elastic.querybuilder import QueryBuilder
from dart.models.Recommendation import Recommendation
from dart.models.Article import Article
import pandas as pd
import matplotlib.pyplot as plt


class StyloMetrics:

    searcher = QueryBuilder()
    df = []

    def __init__(self):
        recommendations = [Recommendation(i) for i in self.searcher.get_all_documents('recommendations')]
        table = []
        for rec in recommendations:
            date = rec.date
            for type in rec.get_recommendation_types():
                for docid in rec.get_articles_for_type(type):
                    article = Article(self.searcher.get_by_id('articles', docid))
                    try:
                        complexity = article.get_style_metric('complexity')
                        nwords = article.get_style_metric('nwords')
                        nsentences = article.get_style_metric('nsentences')
                        table.append([date, type, docid, complexity, nwords, nsentences])
                    except (ValueError, KeyError):
                        continue
        self.df = pd.DataFrame(table)
        self.df.columns = ['date', 'recommender', 'id', 'complexity', 'nwords', 'nsentences']

    def execute(self):
        self.df.boxplot(column='nwords', by='recommender', showfliers=False)
        plt.savefig('../../output/nwords.png')
        self.df.boxplot(column='nsentences', by='recommender', showfliers=False)
        plt.savefig('../../output/nsentences.png')
        self.df.boxplot(column='complexity', by='recommender', showfliers=False)
        plt.savefig('../../output/complexity.png')
        self.df.to_csv('../../output/stylometrics.csv')


def main(argv):
    print("Initializing")
    calculations = StyloMetrics()
    print("Calculating")
    calculations.execute()


if __name__ == "__main__":
    main(sys.argv[1:])
