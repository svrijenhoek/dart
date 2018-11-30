import sys
import pandas as pd
from Elastic.Search import Search
import Util


class NetworkAnalysis:

    searcher = Search()
    results = []

    def add_to_results(self, id1, id2, weight):
        self.results.append(
            {
                'source': id1,
                'target': id2,
                'weight': weight
            }
        )

    def compare_entities(self, df1, df2):
        s2 = pd.DataFrame()
        df1_per = df1[(df1.label == 'PER')]
        df2_per = df2[(df2.label == 'PER')]
        if len(df1_per) > 0 and len(df2_per) > 0:
            s1 = pd.merge(df1_per, df2_per, how='inner', on=['text'])
            s2 = s1.drop_duplicates(subset='text')
        return s2

    def execute(self):
        size = 100
        offset_x = 0
        docs_x = self.searcher.get_all_documents_with_offset('articles', size, offset_x)
        while len(docs_x) > 0:
            count = offset_x
            for doc_x in docs_x:
                count += 1
                print(count)
                try:
                    dfx = pd.DataFrame.from_dict(doc_x['_source']['entities'])
                    offset_y = offset_x
                    docs_y = self.searcher.get_all_documents_with_offset('articles', size, offset_y)
                    while len(docs_y) > 0:
                        for doc_y in docs_y:
                            dfy = pd.DataFrame.from_dict(doc_y['_source']['entities'])
                            if len(dfx) > 0 and len(dfy) > 0:
                                s1 = self.compare_entities(dfx, dfy)
                                if len(s1) > 0:
                                    id1 = doc_x['_id']
                                    id2 = doc_y['_id']
                                    weight = len(s1)
                                    self.add_to_results(id1, id2, weight)
                        offset_y += size
                        docs_y = self.searcher.get_all_documents_with_offset('articles', size, offset_y)
                except KeyError:
                    continue
            offset_x += size
            docs_x = self.searcher.get_all_documents_with_offset('articles', size, offset_x)
        Util.write_to_json('graph.json', self.results)
        print(self.results)


def main(argv):
    calculations = NetworkAnalysis()
    calculations.execute()


if __name__ == "__main__":
    main(sys.argv[1:])
