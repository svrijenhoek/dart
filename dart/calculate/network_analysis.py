import sys
import pandas as pd
from dart.helper.elastic.querybuilder import QueryBuilder
from dart.Article import Article
import dart.Util as Util


class NetworkAnalysis:

    searcher = QueryBuilder()
    checked_list = []
    results = []

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

    def compare_to_all_documents(self, docx):
        dfx = pd.DataFrame.from_dict(docx.entities)
        size = 2000
        sid, scroll_size = self.searcher.get_all_documents_with_offset('articles', size)
        while scroll_size > 0:
            page = self.searcher.scroll(sid, '2m')
            # Update the scroll ID
            sid = page['_scroll_id']
            # Get the number of results that we returned in the last scroll
            documents = page['hits']['hits']
            scroll_size = len(documents)
            self.iterate(dfx, docx.id, documents)

    def iterate(self, dfx, idx, documents):
        for entry in documents:
            docy = Article(entry)
            if docy.id not in self.checked_list:
                dfy = pd.DataFrame.from_dict(docy.entities)
                if len(dfx) > 0 and len(dfy) > 0:
                    # number of unique entities they have in common
                    s = self.compare_entities(dfx, dfy)
                    if s > 0:
                        self.add_to_results(idx, docy.id, s)

    def execute(self):
        size = 2000
        sid, scroll_size = self.searcher.get_all_documents_with_offset('articles', size)
        while scroll_size > 0:
            page = self.searcher.scroll(sid, '2m')
            # Update the scroll ID
            sid = page['_scroll_id']
            # Get the number of results that we returned in the last scroll
            documents = page['hits']['hits']
            for entry in documents:
                document = Article(entry)
                self.compare_to_all_documents(document)
                self.checked_list.append(document.id)
                Util.write_to_json('..\..\output\graph\\result_'+document.id+'.json', self.results)
            scroll_size = len(documents)


def main(argv):
    calculations = NetworkAnalysis()
    calculations.execute()


if __name__ == "__main__":
    main(sys.argv[1:])
