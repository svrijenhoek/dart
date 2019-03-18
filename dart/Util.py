import json
import hashlib
import numpy as np
import random
import string


def read_config_file(top, key):
    with open('config.json') as json_data_file:
        data = json.load(json_data_file)
    return data[top][key]


def read_full_config_file():
    dictionary = {}
    dictionary['append'] = read_config_file('append', 0)
    dictionary['metrics'] = read_config_file('metrics', 0)
    dictionary['articles_folder'] = read_config_file('articles', 'folder')
    dictionary['articles_schema'] = read_config_file('articles', 'alternative_schema')

    dictionary['user_folder'] = read_config_file('user', 'folder')
    dictionary['user_load'] = read_config_file('user', 'load')
    dictionary['user_schema'] = read_config_file('user', 'schema')
    dictionary['user_number'] = read_config_file('user', 'number_of_users')
    dictionary['user_topics'] = read_config_file('user', 'average_topical_interest')
    dictionary['user_spread'] = read_config_file('user', 'average_spread_per_interest')
    dictionary['user_popular'] = read_config_file('user', 'size_popular_stories')
    dictionary['user_random'] = read_config_file('user', 'size_random')

    dictionary['recommendations_folder'] = read_config_file('recommendations', 'folder')
    dictionary['recommendations_load'] = read_config_file('recommendations', 'load')
    dictionary['recommendations_schema'] = read_config_file('recommendations', 'schema')
    dictionary['baseline_recommendations'] = read_config_file('recommendations', 'baseline_recommendations')
    dictionary['recommendation_range'] = read_config_file('recommendations', 'range')
    dictionary['recommendation_size'] = read_config_file('recommendations', 'size')
    dictionary['recommendation_dates'] = read_config_file('recommendations', 'dates')
    return dictionary


def random_string(N):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))


def get_random_number(mean, sdev):
    return int(np.random.normal(mean, sdev))


def generate_hash(s):
    return hashlib.sha2(s.encode('utf-8')).hexdigest()


def write_to_json(file, s):
    with open(file, 'w') as outfile:
        json.dump(s, outfile, indent=4, separators=(',', ': '), sort_keys=True)


def read_json_file(file):
    with open(file) as F:
        return json.load(F)


