import json
import numpy as np
import random
import string
import pandas
import os

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(ROOT_DIR)


def read_config_file():
    with open(os.path.join(BASE_DIR, 'config.json')) as json_data_file:
        data = json.load(json_data_file)
    return data


def read_full_config_file():
    data = read_config_file()
    dictionary = {}
    dictionary['facebook_client_id'] = data['facebook']['client_id']
    dictionary['facebook_client_secret'] = data['facebook']['client_secret']
    dictionary['append'] = data['append']
    dictionary['metrics'] = data['metrics']
    dictionary['articles_folder'] = data['articles']['folder']
    dictionary['articles_schema'] = data['articles']['alternative_schema']
    dictionary['articles_schema_location'] = data['articles']['schema']
    dictionary['popularity_file'] = data['articles']['popularity_file']

    dictionary['user_folder'] = data['user']['folder']
    dictionary['user_load'] = data['user']['load']
    dictionary['user_alternative_schema'] = data['user']['alternative_schema']
    dictionary['user_schema'] = data['user']['schema']
    dictionary['user_number'] = data['user']['number_of_users']
    dictionary['user_topics'] = data['user']['average_topical_interest']
    dictionary['user_spread'] = data['user']['average_spread_per_interest']
    dictionary['user_popular'] = data['user']['size_popular_stories']
    dictionary['user_random'] = data['user']['size_random']
    dictionary['user_reading_history_based_on'] = data['user']['reading_history_based_on']

    dictionary['recommendations_folder'] = data['recommendations']['folder']
    dictionary['recommendations_load'] = data['recommendations']['load']
    dictionary['recommendations_schema'] = data['recommendations']['schema']
    dictionary['baseline_recommendations'] = data['recommendations']['baseline_recommendations']
    dictionary['recommendation_range'] = data['recommendations']['range']
    dictionary['recommendation_size'] = data['recommendations']['size']
    dictionary['recommendation_dates'] = data['recommendations']['dates']
    return dictionary


def random_string(N):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))


def get_random_number(mean, sdev):
    return int(np.random.normal(mean, sdev))


def write_to_json(file, s):
    with open(file, 'w') as outfile:
        json.dump(s, outfile, indent=4, separators=(',', ': '), sort_keys=True)


def read_json_file(file):
    with open(file) as F:
        return json.load(F)


def read_csv(file):
    df = pandas.read_csv(file, sep=';', encoding="ISO-8859-1")
    return df


def transform(doc, schema):
    try:
        for key, value in schema.items():
            if value:
                doc[key] = doc.pop(value)
        return doc
    except KeyError:
        pass


