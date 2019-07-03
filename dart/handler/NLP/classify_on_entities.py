from collections import defaultdict
import dart.Util


class Classifier:

    def __init__(self):
        try:
            self.occupation_mapping = dart.Util.read_csv('output/occupations_mapping.csv')
            self.instance_mapping = dart.Util.read_csv('output/instance_mapping.csv')
        except FileNotFoundError:
            self.occupation_mapping = {}
            self.instance_mapping = {}

    def map(self, cue, key):
        if key == 'PER':
            df = self.occupation_mapping
        elif key == 'ORG':
            df = self.instance_mapping
        df1 = df[df.cue == cue]
        try:
            return df1.iloc[0].classification
        except IndexError:
            return 'onbekend'

    def find_type(self, entity, key):
        types = defaultdict(int)
        if key == 'PER' and 'occupations' in entity:
            for occupation in entity['occupations']:
                occupation_type = self.map(occupation, 'PER')
                types[occupation_type] += 1
        if key == 'ORG' and 'instance' in entity:
            for instance in entity['instance']:
                instance_type = self.map(instance, 'ORG')
                types[instance_type] += 1
        if len(types) > 0:
            if 'politiek' in types:
                return 'politiek'
            else:
                max_key = max(types.items(), key=lambda a: a[1])[0]
                return max_key
        else:
            return 'onbekend'

    def classify_type(self, entities):
        types = defaultdict(int)
        persons = [entity for entity in entities if entity['label'] == 'PER']
        organisations = [entity for entity in entities if entity['label'] == 'ORG']

        for person in persons:
            type = self.find_type(person, 'PER')
            if not type == 'onbekend':
                types[type] += 1
        for organisation in organisations:
            type = self.find_type(organisation, 'ORG')
            if not type == 'onbekend':
                types[type] += 1

        if len(types) > 0:
            return max(types.items(), key=lambda a: a[1])[0]
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

