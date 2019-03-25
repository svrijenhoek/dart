import json
import hashlib
import numpy as np
import random
import string


def read_config_file():
    with open('config.json') as json_data_file:
        data = json.load(json_data_file)
    return data


def read_full_config_file():
    data = read_config_file()
    dictionary = {}
    dictionary['append'] = data['append']
    dictionary['metrics'] = data['metrics']
    dictionary['articles_folder'] = data['articles']['folder']
    dictionary['articles_schema'] = data['articles']['alternative_schema']

    dictionary['user_folder'] = data['user']['folder']
    dictionary['user_load'] = data['user']['load']
    dictionary['user_schema'] = data['user']['schema']
    dictionary['user_number'] = data['user']['number_of_users']
    dictionary['user_topics'] = data['user']['average_topical_interest']
    dictionary['user_spread'] = data['user']['average_spread_per_interest']
    dictionary['user_popular'] = data['user']['size_popular_stories']
    dictionary['user_random'] = data['user']['size_random']

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


def generate_hash(s):
    return hashlib.sha1(s.encode('utf-8')).hexdigest()


def write_to_json(file, s):
    with open(file, 'w') as outfile:
        json.dump(s, outfile, indent=4, separators=(',', ': '), sort_keys=True)


def read_json_file(file):
    with open(file) as F:
        return json.load(F)


