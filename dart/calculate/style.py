import sys
from Elastic.Search import Search
import pandas as pd
import matplotlib.pyplot as plt


class StyloMetrics:

    searcher = Search()
    df = []

    def __init__(self):
        recommendations = [
            {'date': i['_source']['date'],
             'types': i['_source']['recommendations']
             } for i in self.searcher.get_all_documents('recommendations')]
        table = []
        for rec in recommendations:
            date = rec['date']
            for type in rec['types']:
                for docid in rec['types'][type]:
                    document = self.searcher.get_by_id('articles', docid)['_source']
                    try:
                        complexity = document['stylometrics']['complexity']
                        nwords = document['stylometrics']['nwords']
                        nsentences = document['stylometrics']['nsentences']
                        table.append([date, type, docid, complexity, nwords, nsentences])
                    except (ValueError, KeyError):
                        continue
        self.df = pd.DataFrame(table)
        self.df.columns = ['date', 'recommender', 'id', 'complexity', 'nwords', 'nsentences']

    def execute(self):
        self.df.boxplot(column='nwords', by='recommender', showfliers=False)
        plt.savefig('output/nwords.png')
        self.df.boxplot(column='nsentences', by='recommender', showfliers=False)
        plt.savefig('output/nsentences.png')
        self.df.boxplot(column='complexity', by='recommender', showfliers=False)
        plt.savefig('output/complexity.png')
        self.df.to_csv('output/stylometrics.csv')


def main(argv):
    print("Initializing")
    calculations = StyloMetrics()
    print("Calculating")
    calculations.execute()


if __name__ == "__main__":
    main(sys.argv[1:])
