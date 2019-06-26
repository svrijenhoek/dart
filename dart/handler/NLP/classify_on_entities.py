from collections import defaultdict
import dart.Util


class Classifier:

    def __init__(self):
        try:
            self.occupation_mapping = dart.Util.read_csv('output/occupations_mapping.csv')
        except FileNotFoundError:
            self.occupation_mapping = {}

    def find_occupation_type(self, occupation):
        df = self.occupation_mapping
        df1 = df[df.occupation == occupation]
        try:
            return df1.iloc[0].classification
        except IndexError:
            return 'onbekend'

    def classify_type(self, entities):
        people_types = defaultdict(int)
        for entity in (entity for entity in entities if entity['label'] == 'PER'):
            types = defaultdict(int)
            if 'occupations' in entity:
                for occupation in entity['occupations']:
                    occupation_type = self.find_occupation_type(occupation)
                    types[occupation_type] += 1
                total = 0
                for item in types:
                    total = total + types[item]
                if 'politiek' in types:
                    people_types['politiek'] += 1
                elif 'financieel' in types and types['financieel'] / total > 0.3:
                    people_types['financieel'] += 1
                else:
                    max_key = max(types.items(), key=lambda a: a[1])[0]
                    people_types[max_key] += 1
            else:
                people_types['onbekend'] += 1
        if len(people_types) > 0:
            return max(people_types.items(), key=lambda a: a[1])[0]
        else:
            return 'onbekend'

    @staticmethod
    def classify_scope(entities):
        loc = 0
        glob = 0
        for entity in (entity for entity in entities if entity['label'] == 'LOC'):
            if 'country_code' in entity:
                if entity['country_code'] == 'NL':
                    loc += 1
                else:
                    glob += 1
        if loc == 0 and glob == 0:
            return 'onbekend'
        elif loc >= glob:
            return 'local'
        else:
            return 'global'

    def classify(self, entities):
        classification = self.classify_type(entities)
        scope = self.classify_scope(entities)
        return classification, scope

